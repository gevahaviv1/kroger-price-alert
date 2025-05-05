import os
import json
import logging
from dotenv import load_dotenv
import requests

# Load .env
load_dotenv()

CLIENT_ID = os.getenv('KROGER_CLIENT_ID')
CLIENT_SECRET = os.getenv('KROGER_CLIENT_SECRET')
TOKEN_URL = 'https://api.kroger.com/v1/connect/oauth2/token'
PRODUCTS_URL = 'https://api.kroger.com/v1/products'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_access_token():
    """Obtain OAuth2 token via Client Credentials flow."""
    payload = {'grant_type': 'client_credentials', 'scope': 'product.compact'}
    try:
        resp = requests.post(
            TOKEN_URL,
            auth=(CLIENT_ID, CLIENT_SECRET),
            data=payload
        )
        resp.raise_for_status()
        token = resp.json().get('access_token')
        if not token:
            raise ValueError('No access_token in response')
        logger.info('Obtained access token')
        return token
    except Exception as e:
        logger.error(f'Error obtaining token: {e}')
        raise

def fetch_products(token: str, term: str, limit: int = 50) -> list:
    """
    Fetch products from Kroger with pagination.
    Returns a list of product dicts.
    """
    headers = {'Authorization': f'Bearer {token}'}
    params = {'filter.term': term, 'filter.limit': limit}

    products = []
    next_url = PRODUCTS_URL

    while next_url:
        try:
            resp = requests.get(next_url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            page_items = data.get('data', [])
            products.extend(page_items)
            logger.info(f'Fetched {len(page_items)} items')

            # Parse Link header for next page
            link = resp.headers.get('Link', '')
            next_url = None
            for part in link.split(','):
                if 'rel="next"' in part:
                    next_url = part.split(';')[0].strip()[1:-1]
                    break
            params = {}  # only needed on first request
        except Exception as e:
            logger.error(f'Error fetching products: {e}')
            break

    return products

def main():
    term = os.getenv('PRODUCT_SEARCH_TERM', 'milk')
    page_limit = int(os.getenv('PRODUCT_PAGE_LIMIT', '50'))

    try:
        token = get_access_token()
        items = fetch_products(token, term, page_limit)
        out_file = f'{term}_products.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
        logger.info(f'Saved {len(items)} products to {out_file}')
    except Exception:
        logger.error('Failed to fetch or save product data')

if __name__ == '__main__':
    main()
