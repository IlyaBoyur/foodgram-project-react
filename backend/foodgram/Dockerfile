FROM python:3.8.5
WORKDIR /code
COPY . .
RUN pip3 install -r requirements.txt
# Install UTF-8 font pack for fpdf
RUN wget -O temp.zip "https://github.com/reingart/pyfpdf/releases/download/binary/fpdf_unicode_font_pack.zip"
RUN unzip temp.zip -d /usr/local/lib/python3.8/site-packages/fpdf
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 
