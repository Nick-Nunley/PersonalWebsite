import argparse
import requests
import re
import html2text
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

    def output_to_markdown(self, html: str) -> None:
        output_path = re.sub('.pdf$', '.md', self.output_path)
        soup = BeautifulSoup(html, 'html.parser')
        # Find the contact/CV header block
        contact_block = soup.find('div', style = lambda value: value and 'border-bottom: 1px solid' in value)
        education_row = soup.find('h4', string = 'Education')
        experience_row = soup.find('h4', string = 'Experience')
        # Go up to their parent .row containers
        education_div = education_row.find_parent('div', class_ = 'row') if education_row else None
        experience_div = experience_row.find_parent('div', class_ = 'row') if experience_row else None
        # Create a new soup fragment with just the desired content
        minimal_soup = BeautifulSoup('<div id="cv-minimal"></div>', 'html.parser')
        container = minimal_soup.find('div')
        if contact_block:
            container.append(contact_block)
        if education_div:
            container.append(education_div)
        if experience_div:
            container.append(experience_div)
        # Convert to markdown
        clean_html = str(minimal_soup)
        markdown = html2text.html2text(clean_html)
        with open(output_path, 'w', encoding = 'utf-8') as out:
            out.write(markdown)

    def render_pdf(self, html: str) -> None:
        HTML(string = html).write_pdf(self.output_path, stylesheets = [self.style_config])

    def main(self) -> None:
        self.html = self.make_request(url = self.url)
        self.html = self.inject_contact_info(html = self.html, contact_html = self.contact_html)
        self.output_to_markdown(html = self.html)
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
