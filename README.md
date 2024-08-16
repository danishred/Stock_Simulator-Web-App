# Stocks Simulator
#### Video Demo:  <https://youtu.be/jjuCVsI0KuA>
## Description:
### General
The project is a web-application. It is simply an application which allows one to
practice trading stocks. But it is not just that as it also contains a section which
can store notes and can be used by multiple users, each having there data kept
separate from the other. Also there is a Motivation section which displays inspiring
quotes from various authors, helping the user to stay motivated.

### Technologies Used:

- HTML
- CSS
- JavaScript
- Bootstrap
- Python
- Flask (Framework)
- Postgresql (Database)
- Redis KV Database (Session Storage)
- Memegen API
- Yahoo API
- other small libraries

### What it does and how?
When you access the homepage it allows you to login if you are an existing user else
you can register yourself from the register section. Each user should provide their
Email and their password should be at least 8 digits long and is stored in the form
of hash inside the database.

After logging in the user is greeted with a **Portfolio** (We will talk about it later).
On the top there is a navbar and starting from left it has the title of webpage and
and is populated with different section as we move towards right namely **Quote**,
**Buy**, **Sell**, **Notes**, **Motivation**, **History** and finally on the upper right corner
there is a dropdown which displays current user's **username**.

Starting with the user dropdown, it consists of options like **Change Password**,
**Log Out**, **Reset Data**.
The 'Change Password' option opens a Modal and allows user
to change their password.
Clicking on 'Log Out' will log the current user out.
'Reset Data' option also opens up a Modal. It resets the following to its default
settings:-

- Your cash back to default
- All the shares you've purchased
- All your notes back to default
- All your purchase history

It does so by clearing the rows of the different tables of the database having the
id value same as current user.

**Portfolio**: clicking on title of webpage shows 'Portfolio'. It basically is a section which stores
information regarding the stocks and shares of stock user possess, its price as well as
its total value along side the cash possessed by the user. The stocks are fetched from
the IexCloud API and it current price is updated on every refresh, reflecting the loss
or profit the user finally made till now. Since this is all virtual there is a section
to add more virtual money if they like to. Using JavaScript a clock is implemented in the
footer which updates in realtime.

**Quote**: This section allows you to quote shares price of any stock using its stocks symbol.

**Buy**: You can buy stocks using this section. The user have to input stocks symbol and no. of
shares. In case user doesn't have enough money the application won't let user buy shares.

**Sell**: Shares of stocks can be sold using this section. User have to select the share symbol
and input the no. of shares to sell.

**Notes**: One can keep notes related to stocks or pretty much anything. Every user has there
unique notes. It is implemented using databases. On the footer of each note the day and time
it was added is displayed. Each note has its seperate delete button which can be used to
delete them individually.

**Motivation**: This section displays inspiring quotes from various authors, helping the user
to stay motivated. It imports a list of dictionar from a .JSON file into a list variable
and through the use of random function in python. It displays the a new random quote
everytime the user presses on show new quote button.

**History**: This contains history of all transactions (buy and sell) made by the current
user in a tabular format.

### Final Thoughts
The project took a lot of time and effort to be completed. I had many more ideas to
improve it further but currently do not possess the stack of skills to do so. I really enjoyed reading documentations and I am proud that I
did it all myself. 

## Thank you for reading...
