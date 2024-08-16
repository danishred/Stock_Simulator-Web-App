# Stock Simulator

## General
The project is a web-application. It fetches live data of Stocks from Yahoo's API and provides one the interface to practice trading in stocks as if they are really doing it, just the money is virtual. 

It also contains a section which can store notes and can be used by
multiple users, each having there data kept separate from the other. 

There is a Motivation section which displays inspiring quotes from various authors, helping the user to stay motivated.

## Technologies Used:
- HTML
- CSS
- JavaScript
- Bootstrap
- Python
- Flask (Framework)
- PostgreSQL (Database)
- Redis KV Database (Session Storage)
- Memegen API
- Yahoo API
- other small libraries

## What it does and how?
When you access the homepage it allows you to login if you are an existing user else
you can register yourself from the register section. Each user should provide their
Email and their password should be at least 8 digits long and is stored in the form
of hash inside the database.
On the top there is a navbar and starting from left it has the title of webpage and
and is populated with different section as we move towards right namely **Quote**,
**Buy**, **Sell**, **Notes**, **Motivation**, **History** and they perform the functions as they are named.

'Reset Data' option also opens up a Modal. It resets the following to its default
settings:

- Your cash back to default
- All the shares you've purchased
- All your notes back to default
- All your purchase history

## Final Thoughts:
-The project took a lot of effort to be completed. 
-Initially I used SQLite3 DB but later on switched to PostgreSQL for deployment constraints. 
-I also refactored the whole codebase months after project creation with MVC Architecture, further increasing understanding and ease of making future changes
-I really enjoyed reading documentations and I am proud that I did it all myself. 

Thank you for reading.
