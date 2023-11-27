import streamlit as st
import mysql.connector
import datetime

# Connect to your MySQL database
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Mukesh77",
    database="onlinevotingdb"
)
try:
    st.session_state.logged_in
except AttributeError:
    st.session_state.logged_in = False

cursor = conn.cursor()


# Streamlit App
st.title("Online Voting System")

# Function to fetch district IDs from the database


def district_id_ui():
    # Fetch district IDs from the Address table
    cursor.execute("SELECT DistrictID, Locality FROM Address")
    districts = cursor.fetchall()

    # Create a list of district options for the selectbox
    district_options = [
        f"{district[0]} - {district[1]}" for district in districts]

    # Display the selectbox in Streamlit
    district_id = st.selectbox("Select District", district_options)

    # Extract the selected DistrictID from the option
    selected_district_id = int(district_id.split(" - ")[0])

    return selected_district_id


# Sign Up Section
st.subheader("Sign Up")
aadhaar = st.text_input("Aadhaar number:", key="aadhaar_input")
fname = st.text_input("First Name:", key="fname_input")
lname = st.text_input("Last Name:", key="lname_input")
mname = st.text_input("Mother Name:", key="mname_input")
fathername = st.text_input("Father Name:", key="fathername_input")
sex = st.selectbox("Gender", ["F", "M", "Other"], key="sex_selectbox")
age = st.number_input("Enter age", key="age_input")
Birthday = st.date_input("Enter birthday", key="birthday_input")
phone = st.text_input("Phone Number:", key="phone_input")
district_id_signup = district_id_ui()
# Add district UI to sign-up section


# cursor.execute("""
#     SELECT COUNT(*)
#     FROM information_schema.triggers
#     WHERE trigger_name = 'voter_table_update_trigger';
# """)

# trigger_exists = cursor.fetchone()[0]

# if not trigger_exists:
#     cursor.execute("""
#         CREATE TRIGGER voter_table_update_trigger
#         BEFORE UPDATE ON Voter_Table
#         FOR EACH ROW
#         BEGIN
#             SET NEW.LastModified = NOW();
#         END;
#     """)

# Commit the changes
# conn.commit()

# Handle Sign Up button click
if st.button("Sign Up"):
    try:
        # Convert the Streamlit date input to a string
        # birthday_str = Birthday.strftime("%Y-%m-%d")

        # Insert data into the database
        cursor.execute("""
            INSERT INTO Voter_Table (AADHAAR, FirstName, LastName, MotherName, Birthday, FatherName, Sex, Age, DistrictID, Phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (aadhaar, fname, lname, mname, Birthday, fathername, sex, age, district_id_signup, phone))
        conn.commit()

        st.success("Signup successful!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    except ValueError:
        st.error("Error: Invalid date format.")
    finally:
        cursor.close()

# Login Section
st.subheader("Login")
aadhaar_login = st.text_input("Aadhaar number:")

# Handle Login button click
if st.button("Login"):
    try:
        # Check if the entered Aadhaar number matches the records in the database
        cursor.execute(
            "SELECT * FROM Voter_Table WHERE AADHAAR = %s", (aadhaar_login,))
        user = cursor.fetchone()

        if user:
            st.success("Login successful!")
            st.session_state.logged_in = True
        else:
            st.error("Invalid Aadhaar number. Please try again.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    # finally:
    #     cursor.close()

# If logged in, proceed to Election Type or Candidate Type
if st.session_state.logged_in:
    # Election Type Section
    st.subheader("Select Election Type")
    cursor.execute("SELECT ElectionID, ElectionType FROM Election_Table")
    elections = cursor.fetchall()
    election_options = [
        f"{election[0]} - {election[1]}" for election in elections]
    selected_election = st.selectbox("Select Election", election_options)

    # Candidate Type Section
    st.subheader("Select Candidate Type")
    cursor.execute("SELECT CandidateTypeID, CandidateType FROM Candidate_Type")
    candidate_types = cursor.fetchall()
    candidate_type_options = [
        f"{c_type[0]} - {c_type[1]}" for c_type in candidate_types]
    selected_candidate_type = st.selectbox(
        "Select Candidate Type", candidate_type_options)

    # Voting Section

    st.subheader("Vote for a Candidate")

    cursor.execute("SELECT CandidateID, AADHAAR, PartyID, ElectionID, DistrictID FROM Candidate_Table WHERE CandidateTypeID = %s",
                   (selected_candidate_type.split(" - ")[0],))
    candidates = cursor.fetchall()
    candidate_options = [
        f"{candidate[0]} - {candidate[1]}" for candidate in candidates]
    selected_candidate = st.selectbox("Select Candidate", candidate_options)

    # Handle Vote button click
if st.button("Vote"):

    # Check if the user has already voted for this candidate
    cursor.execute("SELECT * FROM Result WHERE CandidateID = %s AND DistrictID = %s",
                   (selected_candidate.split(" - ")[0], candidates[0][4]))
    existing_vote = cursor.fetchone()

    if existing_vote:
        # If the user has already voted, update the existing row to increment the vote count
        cursor.execute("""
                UPDATE Result
                SET Vote_Count = Vote_Count + 1
                WHERE CandidateID = %s AND DistrictID = %s
            """, (selected_candidate.split(" - ")[0], candidates[0][4]))
    else:
        # If the user hasn't voted yet, insert a new row
        cursor.execute("""
                INSERT INTO Result (CandidateID, PartyID, DistrictID, Vote_Count)
                VALUES (%s, %s, %s, %s)
            """, (selected_candidate.split(" - ")[0], candidates[0][2], candidates[0][4], 1))  # Assuming vote count starts at 1
    conn.commit()

    st.success("Vote recorded successfully!")


st.header("Aggregative Query")

# Get the total number of votes for each candidate
cursor.execute("""
    SELECT CandidateID, COUNT(*) as vote_count
    FROM Result
    GROUP BY CandidateID
""")
vote_counts = cursor.fetchall()

# Display the results
st.subheader("Total Votes for Each Candidate")
for vote_count in vote_counts:
    st.write(f"Candidate ID: {vote_count[0]}, Total Votes: {vote_count[1]}")


# #Section for Nested Query
st.header("Nested Query")

# Get the details of the candidates who received the maximum votes in each district
cursor.execute("""
    SELECT r.CandidateID, r.DistrictID, r.Vote_Count, c.AADHAAR, c.PartyID
    FROM Result r
    INNER JOIN (
        SELECT DistrictID, MAX(Vote_Count) as MaxVotes
        FROM Result
        GROUP BY DistrictID
    ) max_votes ON r.DistrictID = max_votes.DistrictID AND r.Vote_Count = max_votes.MaxVotes
    INNER JOIN Candidate_Table c ON r.CandidateID = c.CandidateID
""")
max_votes_details = cursor.fetchall()

# Display the results
st.subheader("Candidates with Maximum Votes in Each District")
for details in max_votes_details:
    st.write(
        f"Candidate ID: {details[0]}, District ID: {details[1]}, Vote Count: {details[2]}, AADHAAR: {details[3]}, Party ID: {details[4]}")


# Update and Delete Section


# Update User Section
st.header("Update and Delete User")

# Update User Section
st.subheader("Update User Information")
aadhaar_update_delete = st.text_input("Enter Aadhaar to update or delete:")


# Fetch the user details based on Aadhaar number
cursor.execute("""
    SELECT * FROM Voter_Table WHERE AADHAAR = %s
""", (aadhaar_update_delete,))
user = cursor.fetchone()

if user:
    st.subheader("Update User Information")
    # Assuming the first column is FirstName
    new_username = st.text_input("New Username:", user[1])

    if st.button("Update User"):
        try:
            # Update user information in the Voter_Table
            cursor.execute("""
                UPDATE Voter_Table
                SET FirstName = %s
                WHERE AADHAAR = %s
            """, (new_username, aadhaar_update_delete))
            conn.commit()

            st.success("User information updated successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
else:
    st.error("User not found.")
# Delete User Section
st.subheader("Delete User")
aadhaar_delete = st.text_input("Enter Aadhaar to delete:")

if st.button("Delete User"):
    try:
        # Delete user from Voter_Table
        cursor.execute("""
            DELETE FROM Voter_Table
            WHERE AADHAAR = %s
        """, (aadhaar_delete,))
        conn.commit()

        st.success("User deleted successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
st.header("show result")


def show_result(db_connection):
    # SQL query to get the results
    query = """
        SELECT Result.PartyID, party_table.PartyName, SUM(Vote_Count) AS 'Total_Count'
        FROM Result, party_table
        WHERE party_table.PartyID = Result.PartyID
        GROUP BY Result.PartyID
        ORDER BY Total_Count DESC
    """

    # Execute the query and fetch results
    with db_connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

        # Display results in Streamlit
        if result:
            st.write("\n\tVOTES FOR EACH PARTY\n")
            st.write("|Party ID | Party Name | Count|")
            for row in result:
                st.write(f" | {row[0]  }  | {row[1]  } | {row[2]  }|")
                st.markdown("---")  # Add a horizontal line between rows

            # Add a horizontal line at the end
            st.markdown("---")
        else:
            st.warning("No results available.")


show_result(conn)

# DELIMITER //


# CREATE PROCEDURE UpdatePhoneNumber(IN aadharNumber VARCHAR(20), IN newPhoneNumber VARCHAR(15))
# BEGIN
#     UPDATE Voter_Table
#     SET Phone = newPhoneNumber
#     WHERE AADHAAR = aadharNumber;
# END //

# DELIMITER ;

st.header("Procedure")

# Input form for updating contact information
aadhaar_update_contact = st.text_input("Enter Aadhaar for updating contact:")
new_phone_number = st.text_input(
    "Enter New Phone Number for updating contact:")

# Handle Update Contact button click
if st.button("Update Contact"):
    try:
        # Check if the entered Aadhaar number matches the records in the database
        cursor.execute(
            "SELECT * FROM Voter_Table WHERE AADHAAR = %s", (aadhaar_update_contact,))
        user = cursor.fetchone()

        if user:
            # Update the phone number in the Voter_Table
            cursor.execute("UPDATE Voter_Table SET Phone = %s WHERE AADHAAR = %s",
                           (new_phone_number, aadhaar_update_contact))
            conn.commit()

            # Show the updated Aadhaar and phone number
            st.success(
                f"Contact information updated successfully! Updated Aadhaar: {aadhaar_update_contact}, Updated Phone Number: {new_phone_number}")
        else:
            st.error("Invalid Aadhaar number. Please try again.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

conn.close()