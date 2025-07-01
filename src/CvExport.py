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
            merged_block = merged_block = BeautifulSoup(contact_html, 'html.parser')
            cv_header.replace_with(merged_block)
        return str(soup)

    def inject_skills_section(self, cv_html: str) -> str:
        cv_soup = BeautifulSoup(cv_html, 'html.parser')
        skills_html = self.make_request(url=re.sub('/cv', '/skills', self.url))
        skills_soup = BeautifulSoup(skills_html, 'html.parser')

        # Extract the content section from the skills page (assumes same class structure)
        skills_section = skills_soup.find('div', class_ = 'row g-5 mb-5')
        if not skills_section:
            print('Skills section not found.')
            return str(cv_soup)

        heading = cv_soup.new_tag('h4')
        heading.string = 'Skills'
        wrapper_div = cv_soup.new_tag('div', **{'class': 'row g-5 mb-5 skills-section'})
        col_header = cv_soup.new_tag('div', **{'class': 'col-md-2'})
        col_header.append(heading)
        col_body = cv_soup.new_tag('div', **{'class': 'col-md-10'})

        # Copy over each top-level element from the original skills_section,
        # but strip any hyperlinks
        for child in skills_section.find_all(recursive = False):
            h3 = child.find('h3')
            if h3 and h3.get_text(strip = True) == 'Skills':
                h3.decompose()
            for a in child.find_all('a'):
                a.replace_with(a.get_text(strip = True))
            col_body.append(child)

        wrapper_div.append(col_header)
        wrapper_div.append(col_body)
        experience_section = cv_soup.find_all('div', class_= 'row g-5 mb-5')[-1]
        experience_section.insert_after(wrapper_div)
        return str(cv_soup)

    def output_to_markdown(self, html: str) -> None:
        output_path = re.sub('.pdf$', '.md', self.output_path)
        soup = BeautifulSoup(html, 'html.parser')
        # Find the contact/CV header block
        contact_block = soup.find('div', style = lambda value: value and 'border-bottom: 1px solid' in value)
        summary_row = soup.find('p', class_ = 'lead')
        education_row = soup.find('h4', string = 'Education')
        experience_row = soup.find('h4', string = 'Experience')
        skills_row = soup.find('h4', string = 'Skills')
        # Go up to their parent .row containers
        education_div = education_row.find_parent('div', class_ = 'row') if education_row else None
        experience_div = experience_row.find_parent('div', class_ = 'row') if experience_row else None
        skills_div = skills_row.find_parent('div', class_ = 'row') if skills_row else None
        # Create a new soup fragment with just the desired content
        minimal_soup = BeautifulSoup('<div id="cv-minimal"></div>', 'html.parser')
        container = minimal_soup.find('div')
        if contact_block:
            container.append(contact_block)
        if summary_row:
            container.append(summary_row)
        if experience_div:
            container.append(experience_div)
        if education_div:
            container.append(education_div)
        if skills_div:
            # Convert each <p> inside the skills section into a Markdown bullet
            ul = soup.new_tag('ul')
            for p in skills_div.find_all('p'):
                text = p.get_text(strip = True)
                if not text:
                    continue
                li = soup.new_tag('li')
                li.string = text
                ul.append(li)
            # Create a header for consistency
            h4 = soup.new_tag('h4')
            h4.string = 'Skills'
            container.append(h4)
            container.append(ul)
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
        self.html = self.inject_skills_section(cv_html = self.html)
        self.render_pdf(html = self.html)
        self.output_to_markdown(html = self.html)



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
