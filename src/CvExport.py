import argparse
import requests
from weasyprint import HTML
from bs4 import BeautifulSoup

class DigitalCV:

    def __init__(self, url: str, html: str = None, output_path: str = None, style_config: str = '_sass/override.scss', contact_html: str = None):
        self.url = url
        if html is None:
            html = ''
        self.html = html
        if output_path is None:
            output_path = 'output.pdf'
        self.output_path = output_path
        self.style_config = style_config
        if contact_html is None:
            contact_html = f"""
                <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #ccc; padding-bottom: 0.25em; margin-bottom: 1em;">
                    <div style="font-size: 16pt; font-weight: 700; margin: 0;">CV</div>
                    <div style="font-size: 10pt;">
                        <a href="https://nick-nunley.github.io/PersonalWebsite/"><strong>Nicholas M. Nunley</strong></a> &nbsp;|&nbsp;
                        <a href="mailto:nicknunley17@ucla.edu">nicknunley17@ucla.edu</a> &nbsp;|&nbsp;
                        <a href="https://github.com/Nick-Nunley">GitHub</a> &nbsp;|&nbsp;
                        <a href="https://www.linkedin.com/in/nicholas-nunley/">Linkedin</a> &nbsp;|&nbsp;
                        Los Angeles, CA
                    </div>
                </div>
                """
        self.contact_html = contact_html

    def make_request(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def inject_contact_info(self, html: str, contact_html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        # Find the 'CV' header element
        cv_header = soup.find('h3', string='CV')
        if cv_header:
            # Create a combined HTML block inside a new container
            merged_block = merged_block = BeautifulSoup(self.contact_html, 'html.parser')
            cv_header.replace_with(merged_block)
        return str(soup)

    def render_pdf(self, html: str) -> None:
        HTML(string = html).write_pdf(self.output_path, stylesheets = [self.style_config])

    def main(self) -> None:
        self.html = self.make_request(url = self.url)
        self.html = self.inject_contact_info(html = self.html, contact_html = self.contact_html)
        self.render_pdf(html = self.html)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c',
        '--cv_url',
        default = 'https://nick-nunley.github.io/PersonalWebsite/cv',
        type = str,
        help = 'Path to CV'
        )

    parser.add_argument(
        '-o',
        '--output',
        default = 'assets/CV_NickNunley.pdf',
        type = str,
        help = 'Path to output CV in .PDF format'
        )

    args = parser.parse_args()

    cv = DigitalCV(
        url = args.cv_url,
        output_path = args.output
        )

    cv.main()
