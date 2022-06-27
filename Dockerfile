FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install vim -y
COPY . .

RUN pip install pygit2
RUN pip install scipy
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD [ "./script_typeAnnotation_analysis.py" ]
