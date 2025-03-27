FROM elasticsearch:7.14.0

# Add configuration for persistence
COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

# Set permissions
USER root
RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/config/elasticsearch.yml
USER elasticsearch

# Expose the required port used by elasticsearch
EXPOSE 9200 9300
