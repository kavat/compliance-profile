FROM centos:7

RUN yum install epel-release -y && \
    yum update -y && \
    yum install -y git && \
    yum install -y jq && \
    yum install -y python3 && \
    yum install -y python3-pip && \
    yum install -y python3-devel && \
    yum clean all

RUN curl https://omnitruck.chef.io/install.sh | bash -s -- -P inspec

WORKDIR /opt

RUN mkdir profiles-inspec

COPY launch_inspec.sh launch_inspect.sh
COPY requests.sh post_requests.sh
COPY app.py app.py
COPY inspec.py inspec.py
COPY config.py config.py
COPY start.sh start.sh
COPY requirements.txt requirements.txt

RUN pip3 install --user -r requirements.txt
RUN chmod +x start.sh
RUN mkdir ./logs

ENTRYPOINT ["/opt/start.sh"]

EXPOSE 5000/tcp
