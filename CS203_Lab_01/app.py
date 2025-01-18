import json
import os
import time
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import SpanKind

# Initialize Flask app and OpenTelemetry
app = Flask(__name__)
app.secret_key = 'secret'

# Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This class is used to format the log messages in JSON format
class JSONFormatter(logging.Formatter):
    def format(self, record):
        current_span = trace.get_current_span() # Getting the current span
        span_context = current_span.get_span_context() if current_span else None 
        trace_id = format(span_context.trace_id) if span_context else None # Getting the trace id
        span_id = format(span_context.span_id) if span_context else None 

        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": trace_id,
            "span_id": span_id,
        } 
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)  # Returns the log data as JSON string

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(JSONFormatter())
logger.addHandler(stream_handler)

# OpenTelemetry Setup
resource = Resource.create({"service.name": "course-catalog-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Jaeger Exporter Setup
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Console Span Exporter to print trace logs to the terminal
console_span_exporter = ConsoleSpanExporter()
console_span_processor = BatchSpanProcessor(console_span_exporter)
trace.get_tracer_provider().add_span_processor(console_span_processor)

# Flask Instrumentation
FlaskInstrumentor().instrument_app(app)

# Metrics Setup
reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter(__name__)

# Define Metrics
route_request_counter = meter.create_counter(
    "route_requests_total",
    unit="1",
    description="Counts the number of requests for each route",
)

# Define Error Counter
error_counter = meter.create_counter(
    "error_count_total",
    unit="1",
    description="Counts the number of different errors",
)

# Utility Functions
COURSE_FILE = 'course_catalog.json'

def load_courses():
    if not os.path.exists(COURSE_FILE):
        logger.warning("Course file not found; returning an empty list.")
        return []
    with open(COURSE_FILE, 'r') as file:
        return json.load(file)


def save_courses(data):
    courses = load_courses()
    courses.append(data)
    with open(COURSE_FILE, 'w') as file:
        logger.info("Saving courses to file.")
        json.dump(courses, file, indent=4)

# Routes
@app.route('/')
def index():
    with tracer.start_as_current_span("index-route", kind=SpanKind.SERVER) as span: # Start a trace span for the "index-route" to monitor server-side operations.
        start_time = time.time() 
        route_request_counter.add(1, {"route": "/", "method": request.method}) # Incrementing the route request counter by 1.

        span.add_event("Rendering index page")  # Adding an event to the span to log that the index page rendering has started.
        span.set_attributes({
            "http.method": request.method,    # The HTTP method used for the request (e.g., GET, POST).
            "http.route": "/",
            "user.ip": request.remote_addr,    # The IP address of the user making the request.
            "message": "Index page rendered successfully."
        })

        logger.info({
            "event": "Index_page_rendered",
            "user_ip": request.remote_addr,
            "message": "Index page rendered successfully."
        })

        processing_time = time.time() - start_time   # Calculating the processing time for rendering the page.
        span.set_attribute("processing_time", processing_time)   # Attaching the processing time to the span
        return render_template('index.html')


@app.route('/catalog')
def course_catalog():
    start_time = time.time()
    with tracer.start_as_current_span("course-catalog", kind=SpanKind.SERVER) as span:
        route_request_counter.add(1, {"route": "/catalog", "method": request.method})   # Incrementing the request counter for monitoring, with metadata for route and method.

        courses = load_courses()
        span.set_attributes({
            "http.method": request.method,    # HTTP method used (e.g., GET).
            "http.url": request.url,
            "user.ip": request.remote_addr,
            "courses.count": len(courses),     # Number of courses loaded.
            "message": "Course catalog loaded successfully."
        })

        processing_duration = time.time() - start_time
        span.set_attribute("processing.duration", processing_duration)

        logger.info({
            "event": "Course_catalog_loaded",
            "courses_count": len(courses),    # Number of courses loaded.
            "user_ip": request.remote_addr,
            "duration": processing_duration,
        })

        return render_template('course_catalog.html', courses=courses)


@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    with tracer.start_as_current_span("add-course", kind=SpanKind.SERVER) as span:
        route_request_counter.add(1, {"route": "/add_course", "method": request.method})

        if request.method == 'POST':
            all_fields = ['code', 'name', 'instructor', 'semester', 'schedule', 'classroom', 'prerequisites', 'grading', 'description']
            required_fields = ['code', 'name', 'instructor']
            course_data = {field: request.form.get(field) for field in all_fields}
            missing_fields = [field for field, value in course_data.items() if not value and field in required_fields]

            if missing_fields:
                error_counter.add(1, {"error_type": "missing_required_fields"})
                span.set_attributes({
                    "error.missing_fields": missing_fields,
                    "message": "User attempted to submit the form with missing required fields."
                })     # Adding error details to the span.

                logger.error({
                    "event": "Missing_required_fields",
                    "missing_fields": missing_fields,
                    "message": "User attempted to submit the form with missing required fields."
                })   # Logs the error details for debugging.

                flash(f"Missing required fields: {', '.join(missing_fields)}.", "error")
                return render_template('add_course.html')

            save_courses(course_data)
            span.set_attributes({
                **course_data,
                "message": f"Course '{course_data['name']}' added successfully."
            })  # Adding course details to the span.

            logger.info({
                "event": "Course_added",
                "course_data": course_data,
                "message": f"Course '{course_data['name']}' added successfully."
            })  # Logs course addition.

            flash(f"Course '{course_data['name']}' added successfully!", "success")
            return redirect(url_for('course_catalog'))

        span.set_attribute("message", "Add course form rendered successfully.")  # Handling the GET request to render the form.
        logger.info({
            "event": "Add_course_form_rendered",
            "message": "Add course form rendered successfully."
        })
        return render_template('add_course.html')


@app.route('/course/<code>')
def course_details(code):
    with tracer.start_as_current_span("course-details", kind=SpanKind.SERVER) as span:
        route_request_counter.add(1, {"route": f"/course/{code}", "method": request.method})

        courses = load_courses()
        course = next((c for c in courses if c['code'] == code), None)

        if not course:
            error_counter.add(1, {"error_type": "course_not_found"})   # Incrementing error counter for "course not found" errors.
            span.set_attributes({
                "error.message": f"No course found with code '{code}'.",
                "message": "Course not found error encountered."
            })  # Adding error details to the span.

            logger.error({
                "event": "Course_not_found",
                "course_code": code,
                "message": f"No course found with code '{code}'."
            })   # Logs error details

            flash(f"No course found with code '{code}'", "error")
            return redirect(url_for('course_catalog'))

        span.set_attributes({
            "course.code": code,  # The code of the course being accessed.
            "course.name": course.get("name"),
            "message": "Course details rendered successfully."
        })       # Adding course details to the span for success tracking.

        logger.info({
            "event": "Course_details_rendered",
            "course_code": code,
            "course_name": course.get("name"),
            "message": "Course details rendered successfully."
        })

        return render_template('course_details.html', course=course)


# Error Handling
@app.errorhandler(404)
def page_not_found(error):
    logger.error({
        'event': 'Page_not_found',
        'path': request.path,
        'user_ip': request.remote_addr
    })     # Logs the error details with event type, requested path, and user IP.

    return render_template(
        'error.html',
        error_type="404 - Page Not Found",
        error_message="Oops! The page you are looking for doesn't exist.",
        description="Sorry, we couldn't find what you're looking for."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    logger.exception({
        'event': 'Internal_server_error',
        'path': request.path,
        'user_ip': request.remote_addr
    })      # Logs the exception details with event type, requested path, and user IP

    return render_template(
        'error.html',
        error_type="500 - Server Error",
        error_message="Oops! Something went wrong.",
        description="Please try refreshing the page or come back later."
    ), 500


@app.errorhandler(Exception)
def handle_exception(error):
    logger.exception({
        'event': 'Unhandled_exception',
        'error_type': type(error).__name__,
        'error_message': str(error),
        'path': request.path,
        'user_ip': request.remote_addr
    })   # Log the exception details for debugging and monitoring.
    
    return render_template(
        'error.html',
        error_type="Unexpected Error",
        error_message="Something went wrong.",
        description="Please try again later or contact support."
    ), 500


# Main Entry Point
if __name__ == "__main__":
    logger.info("Starting Flask application.")
    app.run(debug=True)
