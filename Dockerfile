FROM python:3.7.2
RUN pip install --upgrade pip
#install the needed libraries
RUN pip install ipython
WORKDIR /app
RUN mkdir /app/files
COPY requirements.txt /app
RUN pip install -r requirements.txt
RUN pip3 install slackclient
#add the needed python files
COPY getref_bot.py /app
COPY slack_response.py /app
COPY bqutil.py /app
#add the needed data files
COPY books_of_the_bible.json /app/files
COPY open_bible.png /app/files
CMD python3 getref_bot.py