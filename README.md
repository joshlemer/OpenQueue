# OpenQueue
OpenQueue is a web application, found at [openqueue.rocks](http://www.openqueue.rocks), that allows users to create queues for resources, line up to use them, and see who else is using which resources or who's in line to use them.

OpenQueue is written in the Python-Flask back end framework, uses MongoDB as its database, and uses Bootstrap and Angular for the front end.

To see a quick demonstration, check out this video tour
[![OpenQueue Intro Video](http://img.youtube.com/vi/wC44A8lMA9w/0.jpg)](http://www.youtube.com/watch?v=wC44A8lMA9w)

(At the time of recording, OpenQueue was called QueueMe)

## Installation

These instructions are for Ubuntu-based operating systems.

[Install MongoDB](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/):
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get install mongodb-org
```

Verify that MongoDB is installed
```
mongo --version
```
This should output something like `MongoDB shell version 3.0.2`

Ensure you have these dependencies
```
sudo apt-get install python python-dev git python-virtualenv
```

Clone this repository
```
git clone https://www.github.com/OpenQueue/OpenQueue
cd OpenQueue
```

Create and use a new virtual environment
```
virtualenv OpenQueueVenv
source OpenQueueVenv/bin/activate
```

Install various application-specific dependencies
```
pip install -r requirements.txt
```

Run the development server
```
python manage.py runserver
```

You should now have an instance of OpenQueue running on [localhost:5000](http://localhost:5000/), using the mongodb database `openqueue`.

