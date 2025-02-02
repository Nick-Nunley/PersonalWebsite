import re
import requests
import yaml
import os


class Publications:

    def __init__(self, orcid_id: str, base_url: str = 'https://pub.orcid.org/', orcid_vers: str = 'v3.0', headers = None):
        self.orcid_id = orcid_id
        self.base_url = base_url
        self.orcid_vers = orcid_vers
        if headers is None:
            self.headers = {'Accept': 'application/json'}

    def sanitize_url(self, url: str) -> str:
        return re.sub(r'(?<!:)//+', '/', url)

    # Fetch contributors for a specific work
    def fetch_contributors(self, work_path: str) -> list[str]:
        try:
            detailed_url = f'{self.base_url}/{work_path}'
            detailed_url = self.sanitize_url(detailed_url)
            response = requests.get(detailed_url, headers = self.headers)
            response.raise_for_status()

            # Parse the JSON response
            work_details = response.json()
            contributors = work_details.get('contributors', {}).get('contributor', [])

            # Extract author names
            author_list = [
                contrib.get('credit-name', {}).get('value', 'Unknown Author')
                for contrib in contributors
                ]
            return author_list
        except requests.RequestException as e:
            print(f'An error occurred while fetching contributors: {e}')
            return []

    # Fetch publications
    def fetch_publications(self) -> list[dict[str]]:
        try:
            base_url = f'{self.base_url}/{self.orcid_vers}/{self.orcid_id}/works'
            base_url = self.sanitize_url(base_url)
            response = requests.get(base_url, headers = self.headers)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            works = data.get('group', [])

            publications = []
            for work_group in works:
                work_summary = work_group.get('work-summary', [])
                for summary in work_summary:
                    # Fetch title
                    title = (
                        summary.get('title', {}).get('title', {}).get('value', 'No Title')
                        )
                    # Fetch publication year
                    pub_year = (
                        summary.get('publication-date', {})
                        .get('year', {})
                        .get('value', 'No Year')
                        )
                    # Fetch external identifiers (e.g., DOI)
                    external_ids = summary.get('external-ids', {}).get('external-id', [])
                    identifiers = {
                        ext.get('external-id-type'): ext.get('external-id-value')
                        for ext in external_ids
                        }

                    if 'doi' in identifiers:
                        url = f"https://doi.org/{identifiers['doi']}"
                    else:
                        url = None

                    # Fetch author/contributor list
                    detailed_url = summary.get('path')
                    contributors = self.fetch_contributors(detailed_url)

                    publications.append({
                        'name': title,
                        'publication_year': pub_year,
                        'identifiers': identifiers,
                        'authors': contributors,
                        'url': url,
                        })
            return publications
        except requests.RequestException as e:
            print(f'An error occurred: {e}')
            return []


if __name__ == '__main__':

    # Your ORCID ID
    orcid_id = os.environ.get('ORCID')
    orcid_id = '0009-0007-2368-1653'
    # ORCID API endpoint for public data

    # Initialize the Publications object
    publications = Publications(orcid_id = orcid_id)
    # Retrieve and print publications
    publications = publications.fetch_publications()

    print(yaml.dump(publications, sort_keys = False, default_flow_style = False, allow_unicode = True))
