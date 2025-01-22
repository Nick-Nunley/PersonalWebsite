import requests
import yaml
import os

if __name__ == '__main__':

    # Your ORCID ID
    orcid_id = os.environ.get('ORCID')
    # ORCID API endpoint for public data

    # Set headers for the API request
    headers = {
        "Accept": "application/json",  # Requesting JSON response
    }


    # Fetch publications
    def fetch_publications(orcid_id):
        try:
            base_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Parse the JSON response
            data = response.json()
            works = data.get("group", [])

            publications = []
            for work_group in works:
                work_summary = work_group.get("work-summary", [])
                for summary in work_summary:
                    # Fetch title
                    title = (
                        summary.get("title", {}).get("title", {}).get("value", "No Title")
                    )

                    # Fetch publication year
                    pub_year = (
                        summary.get("publication-date", {})
                        .get("year", {})
                        .get("value", "No Year")
                    )

                    # Fetch external identifiers (e.g., DOI)
                    external_ids = summary.get("external-ids", {}).get("external-id", [])
                    identifiers = {
                        ext.get("external-id-type"): ext.get("external-id-value")
                        for ext in external_ids
                    }

                    if "doi" in identifiers:
                        url = f"https://doi.org/{identifiers['doi']}"
                    else:
                        url = None

                    # Fetch author/contributor list
                    detailed_url = summary.get("path")
                    contributors = fetch_contributors(detailed_url)

                    publications.append({
                        "name": title,
                        "publication_year": pub_year,
                        "identifiers": identifiers,
                        "authors": contributors,
                        "url": url,
                    })

            return publications

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return []


    # Fetch contributors for a specific work
    def fetch_contributors(work_path):
        try:
            detailed_url = f"https://pub.orcid.org{work_path}"
            response = requests.get(detailed_url, headers=headers)
            response.raise_for_status()

            # Parse the JSON response
            work_details = response.json()
            contributors = work_details.get("contributors", {}).get("contributor", [])

            # Extract author names
            author_list = [
                contrib.get("credit-name", {}).get("value", "Unknown Author")
                for contrib in contributors
            ]
            return author_list

        except requests.RequestException as e:
            print(f"An error occurred while fetching contributors: {e}")
            return []


    # Retrieve and print publications
    publications = fetch_publications(orcid_id)

    print(yaml.dump(publications, sort_keys=False, default_flow_style=False, allow_unicode=True))
