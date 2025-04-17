from elasticsearch import Elasticsearch
import time
import requests

# Function to wait for Elasticsearch to be ready
def wait_for_elasticsearch(host="elasticsearch", port=9200, timeout=60):
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"http://{host}:{port}")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > timeout:
                raise TimeoutError("Elasticsearch did not become available in time")
            time.sleep(2)

# Wait for Elasticsearch to be ready
print("Waiting for Elasticsearch to be ready...")
wait_for_elasticsearch()
print("Elasticsearch is ready")

# Connect to Elasticsearch
es = Elasticsearch(["http://elasticsearch:9200"])

# Create index with the required fields
index_name = "documents"
index_body = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "text": {"type": "text"}
        }
    }
}

# Create the index if it doesn't exist
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_body)
    print(f"Created index '{index_name}'")
else:
    print(f"Index '{index_name}' already exists")

# Sample paragraphs from Wikipedia India page
paragraphs = [
    "India, officially the Republic of India,[j][21] is a country in South Asia. It is the seventh-largest country by area; the most populous country from June 2023 onwards;[22][23] and since its independence in 1947, the world's most populous democracy.[24][25][26] Bounded by the Indian Ocean on the south, the Arabian Sea on the southwest, and the Bay of Bengal on the southeast, it shares land borders with Pakistan to the west;[k] China, Nepal, and Bhutan to the north; and Bangladesh and Myanmar to the east. In the Indian Ocean, India is near Sri Lanka and the Maldives; its Andaman and Nicobar Islands share a maritime border with Thailand, Myanmar, and Indonesia.",
    
    "Modern humans arrived on the Indian subcontinent from Africa no later than 55,000 years ago.[28][29][30] Their long occupation, predominantly in isolation as hunter-gatherers, has made the region highly diverse, second only to Africa in human genetic diversity.[31] Settled life emerged on the subcontinent in the western margins of the Indus river basin 9,000 years ago, evolving gradually into the Indus Valley Civilisation of the third millennium BCE.[32] By 1200 BCE, an archaic form of Sanskrit, an Indo-European language, had diffused into India from the northwest.[33][34] Its hymns recorded the dawning of Hinduism in India.[35] India's pre-existing Dravidian languages were supplanted in the northern regions.[36] By 400 BCE, caste had emerged within Hinduism,[37] and Buddhism and Jainism had arisen, proclaiming social orders unlinked to heredity.[38] Early political consolidations gave rise to the loose-knit Maurya and Gupta Empires.[39] Widespread creativity suffused this era,[40] but the status of women declined,[41] and untouchability became an organized belief.[l][42] In South India, the Middle kingdoms exported Dravidian language scripts and religious cultures to the kingdoms of Southeast Asia.[43]",
    
    "In the early mediaeval era, Christianity, Islam, Judaism, and Zoroastrianism became established on India's southern and western coasts.[44] Muslim armies from Central Asia intermittently overran India's northern plains.[45] The resulting Delhi Sultanate drew northern India into the cosmopolitan networks of mediaeval Islam.[46] In south India, the Vijayanagara Empire created a long-lasting composite Hindu culture.[47] In the Punjab, Sikhism emerged, rejecting institutionalised religion.[48] The Mughal Empire, in 1526, ushered in two centuries of relative peace,[49] leaving a legacy of luminous architecture.[m][50] Gradually expanding rule of the British East India Company turned India into a colonial economy but consolidated its sovereignty.[51] British Crown rule began in 1858. The rights promised to Indians were granted slowly,[52][53] but technological changes were introduced, and modern ideas of education and public life took root.[54] A pioneering and influential nationalist movement, noted for nonviolent resistance, became the major factor in ending British rule.[55][56] In 1947, the British Indian Empire was partitioned into two independent dominions,[57][58][59][60] a Hindu-majority dominion of India and a Muslim-majority dominion of Pakistan. A large-scale loss of life and an unprecedented migration accompanied the partition.[61]",
    
    "India has been a federal republic since 1950, governed through a democratic parliamentary system. It is a pluralistic, multilingual and multi-ethnic society. India's population grew from 361 million in 1951 to over 1.4 billion in 2023.[62] During this time, its nominal per capita income increased from US$64 annually to US$2,601, and its literacy rate from 16.6% to 74%. A comparatively destitute country in 1951,[63] India has become a fast-growing major economy and hub for information technology services; it has an expanding middle class.[64] Indian movies and music increasingly influence global culture.[65] India has reduced its poverty rate, though at the cost of increasing economic inequality.[66] It is a nuclear-weapon state that ranks high in military expenditure. It has disputes over Kashmir with its neighbours, Pakistan and China, unresolved since the mid-20th century.[67] Among the socio-economic challenges India faces are gender inequality, child malnutrition,[68] and rising levels of air pollution.[69] India's land is megadiverse with four biodiversity hotspots.[70] India's wildlife, which has traditionally been viewed with tolerance in its culture,[71] is supported in protected habitats."
]

# Insert the four paragraphs
for i, text in enumerate(paragraphs, 1):
    # Check if documents already exist
    search_result = es.search(
        index=index_name,
        body={"query": {"match_phrase": {"text": text[:50]}}}
    )
    
    if search_result["hits"]["total"]["value"] == 0:
        es.index(index=index_name, id=str(i), body={"id": str(i), "text": text})
        print(f"Inserted document {i}")
    else:
        print(f"Document {i} already exists")

print("Setup complete!")
