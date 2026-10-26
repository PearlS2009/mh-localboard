# Mountain House Local Board

A free community board for Mountain House residents to post and find jobs, services, items for sale, things they're looking for, and local teams or activities.

## What it does
- Anyone can browse listings without an account.
- Logging in is required to post a listing and to see a poster's contact information.
- Logged-in users can post, edit and delete their own listings. The database enforces that nobody can change someone else's.
- Six listing types: hiring, looking for work, services, for sale, looking to buy, and community.
- Listings expire after 60 days by default (the maximum), and posters can choose an earlier date. Expired listings can be reactivated by their owner.
- Users aged 13 to 17 sign up with a parent or guardian's email as their contact. Under 13 can't create an account.
- Money and safety tips, including a tip of the day.

## Built with
Python, Streamlit, and Supabase (PostgreSQL database and login). The database rules are written in SQL.

## Known limitations
- Refreshing the page logs you out.
- The age check is self-reported and the guardian email isn't verified.
- No photo uploads, report button or in-app messaging yet.

## About this project
I used Claude (Anthropic) as an AI assistant: it suggested the tools, help in code, database rules, and helped with debugging. I came up with the idea and decided what the app should do: the six listing types, the 60-day expiry, the under-13 block, a parent or guardian as the contact for teens, and leaving out photo uploads for safety. I set up the database, ran the setup, and tested the app with several accounts, including a teen account, to make sure one user can't change another's listing. I took the header photo, chose the colors from it, wrote the tips and messages, and made changes such as clearer labels, a wider layout and green notices.
