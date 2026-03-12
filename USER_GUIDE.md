# User Guide: National E-Voting Console System

This guide walks through a full end-to-end workflow: starting the system, logging in as admin, creating a station, registering a voter, setting up a poll, and casting a vote.

---

## 1. Start the application

From the project root, run:

```bash
python e_voting_console_app.py
```

The **E-VOTING SYSTEM** main menu will appear.

---

## 2. Log in as admin

At the **E-VOTING SYSTEM** menu:

- **Enter choice:** `1`

At **ADMIN LOGIN**:

- **Username:** `admin`
- **Password:** `admin123`

---

## 3. Create a voting station (required before voter registration)

From **ADMIN DASHBOARD**:

- **Enter choice:** `6` (Create Voting Station)

Example values:

- **Station Name:** Kampala Central Station  
- **Location/Address:** Kampala Road  
- **Region/District:** Kampala  
- **Voter Capacity:** 500  
- **Station Supervisor Name:** Jane Supervisor  
- **Contact Phone:** 0700000000  
- **Opening Time:** 08:00  
- **Closing Time:** 17:00  

---

## 4. Create a position

From **ADMIN DASHBOARD**:

- **Enter choice:** `10` (Create Position)

Example values:

- **Position Title:** President  
- **Description:** Head of State  
- **Level:** National  
- **Number of winners/seats:** 1  
- **Minimum candidate age [25]:** Press Enter (or type 25)

---

## 5. Create a candidate (must meet eligibility rules)

From **ADMIN DASHBOARD**:

- **Enter choice:** `1` (Create Candidate)

Example eligible candidate:

- **Full Name:** John Candidate  
- **National ID:** CF000001  
- **Date of Birth:** 1980-01-01 (must be at least 25 years old)  
- **Gender:** M  
- **Education:** Choose 1–4 (e.g. 1 for Bachelor's Degree)  
- **Political Party/Affiliation:** Independent  
- **Brief Manifesto/Bio:** Jobs and services  
- **Address / Phone / Email:** Any value  
- **Has Criminal Record? (yes/no):** no  
- **Years of Public Service/Political Experience:** 5  

---

## 6. Create a poll (election)

From **ADMIN DASHBOARD**:

- **Enter choice:** `14` (Create Poll)

Example values:

- **Poll/Election Title:** General Election 2026  
- **Description:** National general election  
- **Election Type:** General  
- **Start Date:** 2026-03-01  
- **End Date:** 2026-03-30  
- **Enter Position IDs (comma-separated):** 1 (or the ID shown for your position)  
- **Use all active stations? (yes/no):** yes  

---

## 7. Assign candidates to the poll (required before opening)

From **ADMIN DASHBOARD**:

- **Enter choice:** `19` (Assign Candidates to Poll)  
- **Enter Poll ID:** 1 (or the ID of the poll you created)

For the position shown:

- **Modify candidates? (yes/no):** yes  
- **Enter Candidate IDs (comma-separated):** 1 (or your candidate ID)  

---

## 8. Open the poll

From **ADMIN DASHBOARD**:

- **Enter choice:** `18` (Open/Close Poll)  
- **Enter Poll ID:** 1  
- When asked to open the poll, answer **yes**.

The poll is now open for voting.

---

## 9. Register a voter

Return to the main **E-VOTING SYSTEM** menu and choose voter registration:

- **Enter choice:** `3` (Register as Voter)

Example voter:

- **Full Name:** Alice Voter  
- **National ID Number:** VN000001  
- **Date of Birth:** 2000-01-01 (must be at least 18 years old)  
- **Gender:** F (or M / Other)  
- **Residential Address / Phone / Email:** Any value  
- **Create Password:** voter123  
- **Confirm Password:** voter123  
- **Select your voting station ID:** 1 (or the ID of the station you created)  

**Important:** Write down the **Voter Card Number** shown after registration. You need it to log in as this voter.

---

## 10. Verify the voter (admin)

Voters must be verified by an admin before they can log in.

Log in as admin again (see step 2), then from **ADMIN DASHBOARD**:

- **Enter choice:** `21` (Verify Voter)  
- Choose **1** to verify a single voter by ID, or **2** to verify all pending voters.

---

## 11. Log in as voter and cast a vote

From the main **E-VOTING SYSTEM** menu:

- **Enter choice:** `2` (Login as Voter)

At **VOTER LOGIN**:

- **Voter Card Number:** The number shown when you registered (step 9)  
- **Password:** voter123  

From **VOTER DASHBOARD**:

- **Enter choice:** `2` (Cast Vote)  
- **Select Poll ID to vote:** 1  

For each position, enter the number of your chosen candidate (or 0 to abstain), then:

- **Confirm your votes? (yes/no):** yes  

Your vote is recorded and a reference code is shown.

---

## 12. Close the poll and view results (admin)

Log in as admin again. From **ADMIN DASHBOARD**:

1. **Close the poll**  
   - **Enter choice:** `18` (Open/Close Poll)  
   - **Enter Poll ID:** 1  
   - Confirm closing with **yes**.

2. **View results**  
   - **Enter choice:** `27` (View Poll Results)  
   - Enter the poll ID to see the tally, bar charts, and turnout.
