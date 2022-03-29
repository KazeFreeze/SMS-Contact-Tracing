# owned by UOD Research
# Programmer: Tapiru, Bernard Jr. G.
# Testing, Diagnosis and Adjustments: Ramos, Jezmer Kyle and Tagasa, Lorenzo Zachary

import sys
import mysql.connector
# import requests
from mysql.connector import Error
# importing time related libraries
import time
from datetime import datetime
# importing module for IP Address
from ipaddress import IPv4Address
# importing module to create a session between Android and PC
from pyairmore.request import AirmoreSession
# starting SMS service of Airmore
from pyairmore.services.messaging import MessagingService
# credentials for MySQL and AirMore
from secrets import inp_host, inp_password, inp_IP, inp_user, inp_database


def connectToMySQL():
    # establish connection to MySQL
    global connection, cursor
    print("Connecting to MySQL")
    connection = None
    for attempt in range(10):
        try:
            connection = mysql.connector.connect(host=inp_host,
                                                 database=inp_database,
                                                 user=inp_user,
                                                 password=inp_password)
        except Exception as e:
            print("Error while connecting to MySQL", e)
            print("Retrying connection after 20 seconds..")
            numAttemptsLeft = 10 - attempt
            print(numAttemptsLeft, " attempts left.")
            time.sleep(20)

    if connection is None:
        print("Failed to connect to MySQL, closing program")
        sys.exit()
    elif connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server Version", db_Info)
        cursor = connection.cursor(buffered=True)
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record[0])
        connection.autocommit = True


def connectToAirMore():
    # establish connection to phone with Airmore
    print("Connecting to AirMore")
    global smsService
    ANDROID_IP = None
    ANDROID_SESSION = None
    for attempt in range(10):
        try:
            ANDROID_IP = IPv4Address(inp_IP)
            ANDROID_SESSION = AirmoreSession(ANDROID_IP)
        except Exception as e:
            print("Error while connecting to AirMore", e)
            print("Retrying connection after 20 seconds..")
            numAttemptsLeft = 10 - attempt
            print(numAttemptsLeft, " attempts left.")
            time.sleep(20)
        else:
            if not ANDROID_SESSION.is_server_running:
                print("Cannot connect to AirMore")
                print("Retrying connection after 20 seconds..")
                numAttemptsLeft = 10 - attempt
                print(numAttemptsLeft, " attempts left.")
                time.sleep(20)
            elif ANDROID_SESSION.is_server_running:
                break

    if ANDROID_SESSION.is_server_running:
        print("Connected to AirMore")
        # initializing SMS service
        smsService = MessagingService(ANDROID_SESSION)
        print("smsService initialized")
    else:
        print("Unable to connect to AirMore, closing program")
        sys.exit()


def changeToUserID(MessagePhone):
    print("Matching user")
    print("Phone number is", str(MessagePhone))
    try:
        cursor.execute("SELECT user_id FROM users WHERE phone_number ='%s'" % MessagePhone)
        TempUserID = cursor.fetchone()
        if TempUserID is None:
            return None
        else:
            print("Match found")
            UserID = int(TempUserID[0])
            print("User ID is", str(UserID))
            return UserID
    except:
        print("No matches")
        pass


def changeToPhone(UserID):
    SQL = "SELECT phone_number FROM users WHERE user_id=%d" % UserID
    cursor.execute(SQL)
    ID = cursor.fetchone()
    return ID[0]


def checkStatus(MessagePhone, UserID):
    print("Checking user status..")
    SQL = "SELECT status_id, status_updated FROM users WHERE user_id=%d" % UserID
    cursor.execute(SQL)
    Status = cursor.fetchone()
    if Status[0] == 3:
        strStatus = "Positive"
    elif Status[0] == 2:
        strStatus = "Exposed"
    elif Status[0] == 1:
        strStatus = 'Negative'
    else:
        strStatus = "none"
    print("User is ", strStatus)
    TextMessage = "Your status is: " + strStatus + "\nLast updated on " + str(Status[1])
    smsService.send_message(MessagePhone, TextMessage)
    time.sleep(1)


def help(MessagePhone, UserID):
    TextMessage1 = ("If you're a new user, please register by typing \n"
                    "'Register'\n\n")
    TextMessage2 = ("To create a zone, type:\n"
                    "'Create <max capacity>'\n"
                    "Use the zone code that you will receive\n"
                    "The default capacity is 50 if you don't assign one.\n"
                    "Note: you can only modify zones which you created\n\n")
    TextMessage3 = ("To change the capacity of a zone:\n"
                    "'Change <zone code> <new capacity>'\n"
                    "(i.e. 'Change 001 25')\n\n")
    TextMessage4 = ("To check the current capacity of a zone, type:\n"
                    "'Check <zone code>'\n"
                    "'Check 001'\n\n")
    TextMessage5 = ("To enter a zone, type:\n"
                    "'Enter <zone code>'\n"
                    "'Enter 001'\n\n"
                    "To exit your current zone, type:\n"
                    "'Exit'\n\n")
    TextMessage6 = ("To update a user's status, type:\n"
                    "'Update <user's contact number> <status> <Month Day Year Time>'\n"
                    "possible status: negative, exposed, positive\n\n")
    TextMessage7 = ("Note for the contact tracer: Input the start date and time of the infectious period\n"
                    "or input the end date and time of the infectious period.\n"
                    "(i.e. 'Update +631234567890 positive June 2 2021 12:00pm')\n\n")
    TextMessage8 = ("To check your status, type:\n"
                    "'Status'\n"
                    "Your status may be negative, exposed, or positive.\n\n")
    TextMessage9 = ("Always wait for a response before replying.\n"
                    "Commands are case-sensitive and space sensitive.")
    TextMessage10 = ("To modify a user's authority level, type:\n"
                     "'Modify <user's contact number> <new auth level>'\n"
                     "1->Subscriber [default], 2->Moderator, 3->Administrator\n"
                     "(i.e. 'Modify +631234567890 2')\n\n")
    if UserID is None:
        smsService.send_message(MessagePhone, TextMessage1)
    else:
        authLevel = getAuthLevel(MessagePhone)[0]
        if authLevel == 1:
            smsService.send_message(MessagePhone, (
                "{0}{1}{2}{3}{4}{5}{6}".format(TextMessage1, TextMessage2, TextMessage3, TextMessage4, TextMessage5,
                                               TextMessage8, TextMessage9)))
        elif authLevel == 2:
            smsService.send_message(MessagePhone, (
                "{0}{1}{2}{3}{4}{5}{6}{7}{8}".format(TextMessage1, TextMessage2, TextMessage3, TextMessage4,
                                                     TextMessage5,
                                                     TextMessage6, TextMessage7, TextMessage8, TextMessage9)))
        elif authLevel == 3:
            smsService.send_message(MessagePhone, (
                "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}".format(TextMessage1, TextMessage2, TextMessage3, TextMessage4,
                                                        TextMessage5, TextMessage6, TextMessage7, TextMessage8,
                                                        TextMessage10, TextMessage9)))
        time.sleep(1)
    print("Helping finished")


def register(MessagePhone):
    cursor.execute("SELECT phone_number FROM users WHERE phone_number ='%s'" % MessagePhone)
    if cursor.fetchone():
        print("Existing account found!")
        TextMessage = "You already have an existing account!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
    else:
        SQL = "INSERT INTO users (phone_number) VALUES ('%s')" % MessagePhone
        cursor.execute(SQL)
        print("Account created!")
        TextMessage = "You are now registered!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)


def create(MessagePhone, MessageContent, UserID):
    print(UserID)
    Capacity = 50
    if len(MessageContent) > 7:
        try:
            Capacity = int(MessageContent.removeprefix('Create '))
        except:
            print("Invalid zone capacity")
            TextMessage = "The zone capacity is invalid. It must be a whole number without extra spaces or " \
                          "characters. "
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
    print("Creating zone with capacity:", Capacity)
    SQL = "INSERT INTO zones (user_id, max_capacity) VALUES ('%s', '%d')" % (UserID, Capacity)
    cursor.execute(SQL)
    print("Zone Created!")
    SQL = "SELECT zone_id FROM zones ORDER BY zone_id DESC"
    cursor.execute(SQL)
    zone_id = cursor.fetchone()
    TextMessage = "Zone with %d maximum capacity is successfully created! Zone ID: %i" % (Capacity, zone_id[0])
    smsService.send_message(MessagePhone, TextMessage)
    time.sleep(1)


def getAuthLevel(MessagePhone):
    print("Retrieving user authority level..")
    UserID = changeToUserID(MessagePhone)
    if UserID is None:
        TextMessage = "You are not registered!\nRegister first!"
        print("User not registered")
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
        return [None, None]
    else:
        SQL = "SELECT auth_level FROM users WHERE user_id=%d" % UserID
        cursor.execute(SQL)
        AuthLevel = cursor.fetchone()
        if AuthLevel[0] == 3:
            Auth = "Administrator"
        elif AuthLevel[0] == 2:
            Auth = "Moderator"
        else:
            Auth = 'Subscriber'
        print("User is a", Auth)
        return [AuthLevel[0], Auth]


def modifyAuth(MessagePhone, MessageContent, UserID):
    authLevel = getAuthLevel(MessagePhone)[0]
    print(str(authLevel))
    if authLevel > 2:
        if len(MessageContent) == 22:
            OtherUserNumber = MessageContent[7:20]
            OtherUserID = changeToUserID(OtherUserNumber)
            if OtherUserID is None:
                TextMessage = "The specified user cannot be found in the database. Please check your input."
                print("User cannot be found")
                smsService.send_message(MessagePhone, TextMessage)
            else:
                try:
                    newAuth = int(MessageContent[21])
                    if newAuth in [1, 2, 3]:
                        SQL = "UPDATE users SET auth_level = %d WHERE user_id = %d" % (newAuth, OtherUserID)
                        cursor.execute(SQL)
                        TextMessage = f"The user's auth level was set to {getAuthLevel(OtherUserNumber)[1]}."
                        TextMessage2 = f"Your auth level was set to {getAuthLevel(OtherUserNumber)[1]} by {MessagePhone}."
                        smsService.send_message(MessagePhone, TextMessage)
                        time.sleep(1)
                        smsService.send_message(OtherUserNumber, TextMessage2)
                        help(OtherUserNumber, OtherUserID)
                    else:
                        TextMessage = ("The auth level should be an integer among 1, 2, and 3.\n"
                                       "Modify <user's contact number> <new auth level>\n"
                                       "1->Subscriber [default], 2->Moderator, 3->Administrator\n"
                                       "(i.e. 'Modify +631234567890 2'\n")
                        print("Invalid Auth Level")
                        smsService.send_message(MessagePhone, TextMessage)
                except:
                    TextMessage = ("The auth level should be an integer among 1, 2, and 3.\n"
                                   "Modify <user's contact number> <new auth level>\n"
                                   "1->Subscriber [default], 2->Moderator, 3->Administrator\n"
                                   "(i.e. 'Modify +631234567890 2'\n")
                    print("Invalid Auth Level")
                    smsService.send_message(MessagePhone, TextMessage)
        else:
            print("Invalid input")
            TextMessage = ("Invalid command format!\n"
                           "Modify <user's contact number> <new auth level>\n"
                           "1->Subscriber [default], 2->Moderator, 3->Administrator\n"
                           "(i.e. 'Modify +631234567890 2'\n")
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
    else:
        print("Insufficient permissions")
        TextMessage = (
            "You have insufficient permissions to use this command. Contact another admin if there was "
            "a mistake.")
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)


def changeZoneCapacity(MessagePhone, MessageContent, UserID):
    MessageSplit = MessageContent.split()
    try:
        ZoneID = int(MessageSplit[1])
    except:
        print("Invalid Zone ID ", MessageSplit[1])
        TextMessage = "You have entered an invalid Zone ID!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
        return
    else:
        print("Zone ID: ", str(ZoneID))
    try:
        newCapacity = int(MessageSplit[2])
    except:
        print("Invalid capacity: ", MessageSplit[2])
        TextMessage = "You have entered an invalid capacity for the zone!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
        return
    else:
        if newCapacity > 1:
            print("New zone capacity: ", str(newCapacity))
        else:
            print("The zone capacity cannot be less than or equal to 1.")
            TextMessage = "The zone capacity should be more than 1!"
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
            return

    SQL = "SELECT user_id FROM zones WHERE zone_id='%d'" % ZoneID
    cursor.execute(SQL)
    ZoneUserID = cursor.fetchone()
    if ZoneUserID is not None:
        if ZoneUserID[0] == UserID:
            print("The zone matches.")
            SQL = "UPDATE zones SET max_capacity = '%d' WHERE zone_id = '%d'" % (newCapacity, ZoneID)
            cursor.execute(SQL)
            print("Zone max capacity change is successful.")
            TextMessage = "Change successful! Zone %d now has a new max capacity of %d" % (ZoneID, newCapacity)
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
        else:
            print("The zone does not belong to the user.")
            TextMessage = "Zone %d is not yours!" % ZoneID
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
    else:
        print("The zone does not exist.")
        TextMessage = "Zone %d does not exist!" % ZoneID
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)


def enter(MessagePhone, MessageContent, UserID):
    SQL = "SELECT zone_presence FROM users WHERE user_id = %d" % UserID
    cursor.execute(SQL)
    isInZone = cursor.fetchone()
    if isInZone[0] != 0:
        print("User is currently inside another zone")
        TextMessage = "You are still in another zone. Exit your zone first."
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
    elif isInZone[0] == 0:
        SQL = "SELECT status_id FROM users WHERE user_id = %d" % UserID
        cursor.execute(SQL)
        Status = cursor.fetchone()
        StatusID = Status[0]

        if StatusID == 3:
            TextMessage = "You are infected, you should isolate and stay at home!"
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)

        if StatusID == 2:
            TextMessage = "You were exposed, you should quarantine or get tested before entering zones!"
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)

        try:
            ZoneID = int(MessageContent.removeprefix('Enter '))
        except:
            print("Invalid zone ID!")
            TextMessage = "Zone does not exist!"
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
        else:
            print("Entering zone ", ZoneID)
            SQL = "SELECT zone_id FROM zones WHERE zone_id = '%s'" % ZoneID
            cursor.execute(SQL)
            validateZoneID = cursor.fetchone()
            if validateZoneID is None:
                print("Zone does not exist!")
                TextMessage = "Zone does not exist!"
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
            else:
                print("Zone Validated")
                SQL = "SELECT max_capacity, current_capacity FROM zones WHERE zone_id = '%s'" % ZoneID
                cursor.execute(SQL)
                Capacity = cursor.fetchone()
                maxCapacity = Capacity[0]
                currentCapacity = Capacity[1]
                if currentCapacity < maxCapacity:
                    SQL = "INSERT INTO visits (user_id, zone_id, exit_time) VALUES ('%d', '%d', NULL)" % (
                        UserID, ZoneID)
                    cursor.execute(SQL)
                    SQL = "UPDATE users SET zone_presence = 1 WHERE user_id = %d" % UserID
                    cursor.execute(SQL)
                    SQL = "UPDATE zones SET current_capacity = current_capacity + 1 WHERE zone_id = '%d'" % ZoneID
                    cursor.execute(SQL)
                    print("Entry logged successfully")
                    TextMessage = "Entry logged successfully"
                    smsService.send_message(MessagePhone, TextMessage)
                    time.sleep(1)
                    if StatusID == 3:
                        print("Positive user is entering the zone.")
                        print("Tracing users in the zone..")
                        SQL = "SELECT user_id FROM visits WHERE user_id != %d AND zone_id = %d AND exit_time is NULL" % (
                            UserID, ZoneID)
                        cursor.execute(SQL)
                        Contacts = cursor.fetchall()
                        if Contacts is not None:
                            print(Contacts)
                            ExposedUsersID = []
                            for user in range(len(Contacts)):
                                ExposedUsersID.append(Contacts[user])
                            notifyExposed(ExposedUsersID)
                    else:
                        print("Scanning zone for positive users..")
                        SQL = "SELECT user_id FROM visits WHERE user_id != %d AND zone_id = %d AND exit_time is NULL" % (
                            UserID, ZoneID)
                        cursor.execute(SQL)
                        UsersInZone = cursor.fetchall()
                        if UsersInZone is not None:
                            isPositiveInZone = False
                            for user in range(len(UsersInZone)):
                                SQL = "SELECT status_id FROM users WHERE user_id = '%d'" % UsersInZone[user]
                                cursor.execute(SQL)
                                UserInZoneStatus = cursor.fetchone()
                                if UserInZoneStatus[user] == 3:
                                    isPositiveInZone = True
                            if isPositiveInZone:
                                ExposedUsersID = []
                                ExposedUsersID.append(UserID)
                                notifyExposed(ExposedUsersID)
                else:
                    TextMessage = "The zone has reached maximum capacity. You cannot enter."
                    smsService.send_message(MessagePhone, TextMessage)
                    time.sleep(1)


def exit(MessagePhone, UserID):
    SQL = "SELECT zone_presence FROM users WHERE user_id = '%d'" % UserID
    cursor.execute(SQL)
    ZonePresence = cursor.fetchone()
    if ZonePresence[0] == 0:
        print("The user is not in a zone.")
        TextMessage = "You are not in a zone!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
    else:
        SQL = "SELECT visit_id, zone_id FROM visits WHERE user_id = %d AND exit_time IS NULL" % UserID
        cursor.execute(SQL)
        Visit = cursor.fetchone()
        VisitID = Visit[0]
        ZoneID = Visit[1]
        SQL = "UPDATE visits SET exit_time = CURRENT_TIMESTAMP() WHERE visit_id = %d" % VisitID
        cursor.execute(SQL)
        SQL = "UPDATE users SET zone_presence = 0 WHERE user_id = %d" % UserID
        cursor.execute(SQL)
        SQL = "UPDATE zones SET current_capacity = current_capacity - 1 WHERE zone_id = '%d'" % ZoneID
        cursor.execute(SQL)
        print("Exit logged successfully")
        TextMessage = "Exit from zone " + str(ZoneID) + " logged successfully"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)


def notifyExposed(ExposedUsersID):
    UsersID = list(dict.fromkeys(ExposedUsersID))
    print("Exposed users: ", UsersID)
    TextMessage = "Warning, you may have been exposed to a positive user. Contact the COVID-19 Inter-Agency Task " \
                  "Force for testing and quarantine assistance.\n\n"
    TextMessage2 = ("DOH Hotlines:\n"
                    "02 894-COVID\n"
                    "02 894-26843\n\n"
                    "For PLDT, SMART, SUN, and TnT Subscribers:\n"
                    "1555")
    print("Locating exposed users..")
    for countx in range(len(UsersID)):
        MessagePhone = changeToPhone(UsersID[countx])
        smsService.send_message(MessagePhone, TextMessage + TextMessage2)
        time.sleep(1)
        SQL = "UPDATE users SET status_id = 2 WHERE user_id = %d" % UsersID[countx]
        cursor.execute(SQL)
    print("Exposed users notified")


def markExposed(UserID, StatusUpdated):
    print("Finding user contact history..")
    print(UserID, StatusUpdated)
    SQL = "SELECT zone_id, entry_time, exit_time FROM visits WHERE user_id = %d AND entry_time >= '%s'" % (
        UserID, StatusUpdated)
    cursor.execute(SQL)
    VisitHistory = cursor.fetchall()
    ExposedUsersID = []
    print("Marking exposed users..")
    for county in range(len(VisitHistory)):
        ZoneID = VisitHistory[county][0]
        print(ZoneID)
        EntryTime = VisitHistory[county][1]
        ExitTime = VisitHistory[county][2]
        print("Finished assignment")
        if ExitTime is not None:
            SQL = "SELECT user_id FROM visits WHERE zone_id = %d AND user_id != %d AND entry_time < '%s' AND exit_time > '%s'" % (
                ZoneID, UserID, ExitTime, EntryTime)
        else:
            SQL = "SELECT user_id FROM visits WHERE zone_id = %d AND (user_id != %d AND entry_time > '%s' OR exit_time > '%s')" % (
                ZoneID, UserID, EntryTime, EntryTime)
        cursor.execute(SQL)
        Contacts = cursor.fetchall()
        print(Contacts)
        for countz in range(len(Contacts)):
            # it may be a 1D array
            ExposedUsersID.append(Contacts[countz][0])
        print(ZoneID)
    print("Finished marking exposed users")
    notifyExposed(ExposedUsersID)


def updateStatus(MessagePhone, MessageContent, UserID):
    authLevel = getAuthLevel(MessagePhone)[0]
    if authLevel == 1:
        TextMessage = "You do not have sufficient permissions. Contact an administrator if there is a concern."
        smsService.send_message(MessagePhone, TextMessage)
    else:
        Status = MessageContent.removeprefix('Update ')
        OtherUserNumber = MessageContent[7:20]
        OtherUserID = changeToUserID(OtherUserNumber)
        if OtherUserID is None:
            TextMessage = "The specified user cannot be found in the database. Please check your input."
            print("User cannot be found")
            smsService.send_message(MessagePhone, TextMessage)
        elif "negative" in Status:
            try:
                StatusUpdated = datetime.strptime(MessageContent[30:], '%B %d %Y %I:%M%p')
                print("negative")
                StatusID = 1
                SQL = "UPDATE users SET status_id = %d, status_updated='%s', updated_by='%s' WHERE user_id = %d" % (
                    StatusID, StatusUpdated, MessagePhone, OtherUserID)
                cursor.execute(SQL)
                TextMessage = "The user's status was updated to negative."
                TextMessage2 = f"Your status was updated to negative by {MessagePhone}"
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
                smsService.send_message(OtherUserNumber, TextMessage2)
                print(StatusUpdated)
            except:
                print("Invalid date!")
                TextMessage = ("Invalid date!\n"
                               "Update <status> <Month Day Year Time>\n"
                               "(i.e. Update negative June 2 2021 3:00pm)\n\n")
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)

        elif "positive" in Status:
            try:
                StatusUpdated = datetime.strptime(MessageContent[30:], '%B %d %Y %I:%M%p')
                print("positive")
                StatusID = 3
                SQL = "UPDATE users SET status_id = %d, status_updated='%s', updated_by='%s' WHERE user_id = %d" % (
                    StatusID, StatusUpdated, MessagePhone, OtherUserID)
                cursor.execute(SQL)
                TextMessage = "The user's status was updated to positive."
                TextMessage2 = f"Your status was updated to positive by {MessagePhone}."
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
                smsService.send_message(OtherUserNumber, TextMessage2)
                time.sleep(1)
                print(StatusUpdated)
                markExposed(UserID, StatusUpdated)
                print("tracing successful")
            except:
                print("Invalid date!")
                TextMessage = ("Invalid date!\n"
                               "Update <user's contact number> <status> <Month Day Year Time>\n"
                               "(i.e. Update +631234567890 positive June 2 2021 3:00pm)\n\n")
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)

        elif "exposed" in Status:
            try:
                StatusUpdated = datetime.strptime(MessageContent[29:], '%B %d %Y %I:%M%p')
                print("exposed")
                StatusID = 2
                SQL = "UPDATE users SET status_id = %d, status_updated='%s', updated_by='%s' WHERE user_id = %d" % (
                    StatusID, StatusUpdated, MessagePhone, OtherUserID)
                cursor.execute(SQL)
                TextMessage = "The user's status was updated to exposed."
                TextMessage2 = f"Your status was updated to exposed by {MessagePhone}."
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
                smsService.send_message(OtherUserNumber, TextMessage2)
                time.sleep(1)
                print(StatusUpdated)
            except:
                print("Invalid date!")
                TextMessage = ("Invalid date!\n"
                               "Update <status> <Month Day Year Time>\n"
                               "(i.e. Update positive June 2 2021 3:00pm)\n\n")
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
        else:
            print("Invalid status!")
            TextMessage = "Invalid status!\nCommands are case-sensitive"
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)


def checkZoneCapacity(MessagePhone, MessageContent, UserID):
    try:
        ZoneID = int(MessageContent.removeprefix('Check '))
    except:
        print("Invalid Zone ID")
        TextMessage = "You have entered an invalid zone code!"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
        return
    else:
        print("Checking zone capacity of zone %d" % ZoneID)
        SQL = "SELECT current_capacity, max_capacity FROM zones WHERE zone_id = '%d'" % ZoneID
        cursor.execute(SQL)
        Capacity = cursor.fetchone()
        try:
            TextMessage = "Zone %d currently has a capacity of %d/%d." % (ZoneID, Capacity[0], Capacity[1])
        except:
            print("Zone %d does not exist!" % ZoneID)
            TextMessage = "Zone %d does not exit!" % ZoneID
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
        else:
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
            print("Zone capacity check is successful.")


def evaluateQuery(MessagePhone, MessageContent):
    numAdminPin = 1234
    strAdminPhone = "+639352273278"
    arrCommandList = ["Help", "Register", "Create", "Change", "Check", "Enter", "Exit", "Update", "Status", "Modify",
                      ("Fix Records " + str(numAdminPin))]
    arrIgnoredSenderList = ["AutoLoadMAX", "8080", "4438", "TM", "GCash"]
    numCommandCount = 0
    UserID = changeToUserID(MessagePhone)
    for command in range(len(arrCommandList)):
        if arrCommandList[command] in MessageContent:
            numCommandCount += 1
    if numCommandCount == 1:
        if "Help" in MessageContent and len(MessageContent) < 5:
            print("Helping ", MessagePhone)
            help(MessagePhone, UserID)
        elif "Register" in MessageContent and len(MessageContent) < 9:
            print("Registering ", MessagePhone)
            register(MessagePhone)
        elif UserID is not None:
            if "Create" in MessageContent:
                print("Creating zone for ", MessagePhone)
                create(MessagePhone, MessageContent, UserID)
            elif "Change" in MessageContent:
                print("Changing zone capacity for ", MessagePhone)
                changeZoneCapacity(MessagePhone, MessageContent, UserID)
            elif "Check" in MessageContent and len(MessageContent) > 6:
                print("Checking zone capacity for ", MessagePhone)
                checkZoneCapacity(MessagePhone, MessageContent, UserID)
            elif "Enter" in MessageContent:
                print(MessagePhone, "is entering a zone.")
                enter(MessagePhone, MessageContent, UserID)
            elif "Exit" in MessageContent and len(MessageContent) < 5:
                print(MessagePhone, "is exiting a zone.")
                exit(MessagePhone, UserID)
            elif "Update" in MessageContent:
                print(MessagePhone, "is updating a user's status.")
                updateStatus(MessagePhone, MessageContent, UserID)
            elif "Status" in MessageContent and len(MessageContent) < 7:
                print(MessagePhone, "is checking their status.")
                checkStatus(MessagePhone, UserID)
            elif "Modify" in MessageContent and len(MessageContent) < 23:
                print(MessagePhone, "is modifying a user's authority level")
                modifyAuth(MessagePhone, MessageContent, UserID)
            elif ("Fix Records " + str(numAdminPin)) in MessageContent and MessagePhone == strAdminPhone:
                fixRecords()
            else:
                print(MessagePhone, "sent invalid keywords.")
                TextMessage = "Invalid keyword!\nCommands are case-sensitive and space sensitive!\nType 'Help' for " \
                              "instructions "
                smsService.send_message(MessagePhone, TextMessage)
                time.sleep(1)
        else:
            TextMessage = "You are not registered!\nRegister first!"
            print("User not registered")
            smsService.send_message(MessagePhone, TextMessage)
            time.sleep(1)
    elif numCommandCount > 1:
        print(MessagePhone, "is requesting too many commands at the same time.")
        TextMessage = "Too many keywords! Use only one command at a time."
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)
    elif MessagePhone in arrIgnoredSenderList:
        pass
    else:
        print(MessagePhone, "sent invalid keywords.")
        TextMessage = "Invalid keyword!\nCommands are case-sensitive and space sensitive!\nType 'Help' for instructions"
        smsService.send_message(MessagePhone, TextMessage)
        time.sleep(1)


def checkInbox():
    print("Checking inbox..")
    messages = smsService.fetch_message_history()
    inbox_items = len(messages)
    print("Total items: ", inbox_items)
    count = 0
    for count in range(0, inbox_items):
        if not messages[count].was_read:
            messages[count].was_read = True
            if len(messages[count].phone) > 7:
                print("Detected new user message")
                MessagePhone = messages[count].phone
                MessageContent = messages[count].content
                # MessageDT = messages[count].datetime
                print(MessageContent)
                evaluateQuery(MessagePhone, MessageContent)
    print("Inbox check finished.")


def updateRecords():
    print("Updating records.. ")
    SQL = "SELECT * FROM visits WHERE datediff(current_timestamp, entry_time) > 21"
    cursor.execute(SQL)
    oldRecords = cursor.fetchone()
    if oldRecords is not None:
        SQL = "DELETE FROM population.visits WHERE datediff(current_timestamp, entry_time) > 21"
        cursor.execute(SQL)
        print("Records older than 21 days have been deleted successfully.")
    print("Records have been updated.")


def fixRecords():
    print("Fixing records.. ")
    SQL = "SELECT user_id, status_id, status_updated FROM users WHERE status_id = 3"
    cursor.execute(SQL)
    positiveUsers = cursor.fetchall()
    if positiveUsers is not None:
        for user in range(len(positiveUsers)):
            markExposed(positiveUsers[user][0], positiveUsers[user][2])


print("SMS Contact Tracing Service")
print("Initializing interfaces..")
connectToMySQL()
connectToAirMore()
print("Initialization successful!")
print("SMS Contact Tracing Service Started\n")
genAttempt = 0
while genAttempt < 5:
    try:
        CheckTime = datetime.today()
        checkInbox()
        print("Time checked: ", CheckTime)
        updateRecords()
    except Exception as e:
        print("Connection issues encountered!", e)
        genAttempt += 1
        leftAttempt = 5 - genAttempt
        print("Retrying after 20 seconds..")
        print(leftAttempt, "attempts left\n")
        time.sleep(20)
    else:
        print("Starting 10 seconds sleep..\n")
        time.sleep(10)
        print("Woke up. Again.")
