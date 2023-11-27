# Election-System-Management-
TABLES
Election Table:
Type: Type of election happening. (In our case: STATE ASSEMBLY - CM)
Id: Id for type of election
Party Table:
Id: Party ID
Name: Party Name
Symbol: Party Symbol
Leader: Party Leader
Candidate Type:
Type: Candidate is applying for which post. (In our case: MLA-Member of Legislative Assembly)
Type ID: Id of post applied for
Candidate Table:
ID: Id for each Candidate
Aadhaar: Candidate’s Aadhaar no.
Type ID: Id of post he is standing for
Party ID: Id of which party he belongs to
Election ID: Id of which type of election is he nominated in
District ID: Id of District in which he is standing for
User Type:
Type: Who is voting Citizen / Candidate
Type ID: Id of Voter
User Table:
It basically Contains Voter information required during login
Is Active: Is the registered voter Alive or Dead
User Type ID: Id of User Type (Citizen / Candidate)
Voter Id: Voter Id of every user
Def_Password: The system generated password that was initially given to the user, which can later be changed
Aadhaar: Aadhaar no. for reference from the Voter Table and connect information of both tables
NOTE: User table is linked with the Voter Table with the common column Aadhaar no. It basically includes the above details every person with the given Aadhaar no.
Voter Table:
Contains Aadhaar No., First Name, Last Name, Mother’s Name, Father’s Name, Sex, Birthday, Age, District ID, Phone No.
It basically contains information during registration of voter
It is linked with the User table with Aadhaar Id
Address:
District ID: Area-wise Id
Locality: Area from where he/she is voting
City & State: City and State of User
Pin code: Pin code of locality of the user
NOTE: This table contains information about the Permanent Address of the Voter
Vote Table:
Vote ID: Auto-assigned Id. (Nothing to do with Citizen)
Voter ID: Who voted, that person’s Voter Id
Party ID: Whom the person voted to
District ID: District ID for the region the person has voted for
Candidate ID: The ID of candidate of the party they voted for
