# Quarterapp

A personal time tracker for keeping track of what activities you spend your time on during the day. It is not like
a traditional time reporting system, which is primarily designed for extracting data. Quarterapp is designed for
putting in data first, and creating reports second.

The idea is to illustrate each day as 24 rows with 4 columns in each row - 23 hours with 4 quarters. Each quarter
can be tied to a specific activity by color. A day can then summarize how much time you spent in total and per
activity. Quarterapp also supports extracting reports spanning more than a day.


## Usage

Start the server using the command: 

    python quarterapp/quarterapp.py


## Test

Run the unit test using nose:

    nosetests


## Configuration

Quarterapp uses a Python configuration file that is expected to be located
in the same directory as quarterapp.py (i.e. its working directory) and
be named quarterapp.conf.

An example configuration file is provided under the name quarterapp.example.conf.


### Cookie

Tornado uses a hased cookie value for your secure cookies. Generate and
specify your unique hash.

    cookie_secret = "123"


### Password salt

Quarterapp will salt any password prior to hashing and storing in database, generate
your unique salt and store it at

    salt = "secret"

Note that you cannot change this salt without loosing the ability to login for all existing users


### MySQL settings

Quarterapp uses the MySQL database and needs the following settings:

    mysql_database = "quarterapp"
    mysql_host = "127.0.0.1:3306"
    mysql_user = "quarterapp"
    mysql_password = "quarterapp"


### E-mail settings

Quarterapp sends e-mail for signups, password reset, etc. and needs the following SMTP settings:

    mail_host = "smtp.example.com"
    mail_port = 465
    mail_from = "no-reply@example.com"
    mail_user = "quarter@example.com"
    mail_password = "secret"


## Installation


### Install on Debian

Install tha needed packages for doing python, MySQL and web by running these commands

    sudo apt-get install python-pip python-dev build-essential
    sudo apt-get install mysql-server
    sudo apt-get install libmysqlclient-dev
    sudo pip install --upgrade pip
    sudo pip install tornado
    sudo pip install mysql-python


### Install on OSX

    pip install tornado
    pip install mysql-python


### Setup the MySQL database.

Login as root by issuing.

    mysql -u root -p

Create the database and a system user.

    create database quarterapp;
    grant all privileges on quarterapp.* to quarterapp@127.0.0.1 identified by 'quarterapp';
    grant all privileges on quarterapp.* to quarterapp@localhost identified by 'quarterapp';

Create the database used for unittesting

    create database quarterapp_test;
    grant all privileges on quarterapp_test.* to quarterapp@127.0.0.1 identified by 'quarterapp';
    grant all privileges on quarterapp_test.* to quarterapp@localhost identified by 'quarterapp';

Run the SQL script to setup the tables needed.

    mysql -u quarterapp -p < quarterapp.sql


### Create package

If you want to create a Distribution of quarterapp you should install these Node tools for doing compression of frontend resources:

    npm install uglify-js -g
    npm install clean-css -g

Then it is a matter of running the package script in the quarterapp root, this will generate a python Distribution based on the setup.py script.

    ./package

This of cource assumes you are running a Unix system.


### Configure

Make a copy the example configuration file and enter your specific details. See section #Usage
for details.


## Contributors

Special thanks to:

Fredrik Håård (haard)
Olof Fredriksson (OlofFredriksson)

## License

Copyright © 2012-2013 Markus Eliasson

Distributed under the BSD License
