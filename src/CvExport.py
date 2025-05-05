import argparse
import requests
from weasyprint import HTML

class DigitalCV:

    def __init__(self, url: str, html: str = None, output_path: str = None, style_config: str = '_sass/override.scss'):
        self.url = url
        if html is None:
            html = ''
        self.html = html
        if output_path is None:
            output_path = 'output.pdf'
        self.output_path = output_path
        self.style_config = style_config

    def make_request(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def render_pdf(self, html: str) -> None:
        HTML(string = html).write_pdf(self.output_path, stylesheets = [self.style_config])

    def main(self) -> None:
        self.html = self.make_request(url = self.url)
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
