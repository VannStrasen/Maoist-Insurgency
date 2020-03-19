import pandas as pd
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup
import nltk  # For natural language processing
import sys  # For exiting safely


# Finds the second instance of a character in a text
def second_char(char, text):
    first = text.find(char)
    if first != -1 and first + 1 < len(text):
        second = text[first + 1:].find(char)
        return second + first
    else:
        # Couldn't find a second instance of a character
        return -1


# Returns the correct month based on an input string
def month_finder(x):
    if x == 0:
        return "Jan"
    if x == 1:
        return "Feb"
    if x == 2:
        return "Mar"
    if x == 3:
        return "Apr"
    if x == 4:
        return "May"
    if x == 5:
        return "Jun"
    if x == 6:
        return "Jul"
    if x == 7:
        return "Aug"
    if x == 8:
        return "Sep"
    if x == 9:
        return "Oct"
    if x == 10:
        return "Nov"
    if x == 11:
        return "Dec"


# Create a dictionary of most populous indian cities and pair it with their
# state. If we can't find anything, might was well search through this dict.
# because there's a good chance it'll be here.
# Defining the two lists that will briefly hold the districts and cities before
# placing them into a dictionary.
state_dict_list = []
city_dict_list = []

# Getting the html
d_list = "https://en.wikipedia.org/wiki/List_of_cities_in_India_by_population"
try:
    d_html = urlopen(d_list)
except URLError:
    sys.exit("URL Error\n" + d_list)
d_bs_obj = BeautifulSoup(d_html.read(), features="html.parser")
d_table = d_bs_obj.findAll('tr')

# Placing the city or state into the correct list.
for d_row in d_table[1:302]:  # Only 300 results
    index = 1  # Holds whether we're working with a city or a state
    for res in d_row.find_all('a'):
        res = res.get_text(strip=True)
        if res[0] == "[":
            # This result is a cite, not a new city/state. So, do nothing
            continue
        elif index == 1:  # A city
            city_dict_list.append(res)
            index = 2
        elif index == 2:
            state_dict_list.append(res)

# Creating the dictionary
city_dictionary = {city_dict_list[i]: state_dict_list[i]
                   for i in range(len(city_dict_list))}


# Given a string, test to see if there's a mention of
# a state inside of the string.
# The statelist is obtained from http://vlist.in
def state_finder(first_sentence_str):
    # Should test for state == N/A on the outside
    statelist = ["Andaman and Nicobar Islands", "Andhra Pradesh",
                 "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh",
                 "Chhattisgarh", "Dadra and Nagar Haveli", "Daman and Diu",
                 "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
                 "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala",
                 "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur",
                 "Meghalaya", "Mizoram", "Nagaland", "Delhi", "Odisha",
                 "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
                 "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
    for state_str in statelist:
        if first_sentence_str.find(state_str) != -1:
            return state_str
    return "N/A (state_finder failed)"


# Declaration of all variables for the dataset
html_list = [None] * 12
date_list = []
event_list = []
actor_list = []
reactor_list = []
state_list = []
district_list = []
village_list = []
police_station_list = []
forest_list = []
report_list = []
summary_list = []

# Ideas:
# Border of _____ | _____-_____ border


# Link to the website:
# https://www.satp.org/terrorist-activity/india-maoistinsurgency-Jan-2019
# You can change the "Jan" to the first 3 letters of the month,
# and the year ranges from 2001 to 2020.
# The website is updated almost daily, so in the beginning of January in 2021,
# the year range will be from 2001 to 2021.

# Necessary to help print progress for conversion to csv
date = ""
year_index = 1
month_index = 1
year_range = range(2018, 2019)  # Used in loop below and also in html loop
year_total = 0
for year in year_range:
    year_total += 1

for year in year_range:
    print("***** Requesting and opening websites *****")
    month_index = 1  # Gotta reset this after each year, else, type error
    for month in range(0, 12):
        month_str = month_finder(month)
        link = "https://www.satp.org/terrorist-activity/" +\
               "india-maoistinsurgency-" + month_str + "-" + str(year)
        print("* " + month_str + " " + str(year))
        try:
            html_list[month] = urlopen(link)
        except URLError:
            sys.exit("URL error")

    print("***** Scraping information from opened websites *****")
    for html in html_list:
        bsObj = BeautifulSoup(html.read(), features="html.parser")

        bs_table = bsObj.findAll('tr')

        month_str = month_finder(month_index - 1)
        try:
            if month_index == 13 or month_index == 1:
                print("***** " + month_str + ", year " + str(year_index) +
                      " out of " + str(year_total))
                year_index += 1
                month_index = 2
            else:
                print("* " + month_str)
                month_index += 1
        except TypeError:
            sys.exit("Type Error")

        # The first value, and the last 5 values, do not hold relevant
        # information, so we ignore them in the loop.
        for row in bs_table[1:-5]:

            # Defining the date column
            date = row.find('td').get_text(strip=True)
            if date.find("&nbsp"):  # For when the dataset says its not one day
                date = date.replace("&nbsp", " through ")
                date = date.replace(" - ", " ")
            date = date + ", " + str(year)  # Add on the year

            # Defining the summary column
            summary = ""
            try:
                summary = row.find('div', {"class": "more"}).\
                    get_text(strip=True)
                summary = summary.replace("\n", " ")
                summary = summary.replace("\t", " ")
                summary = summary.replace("\r", " ")
                summary = summary.replace("Read less...", "")
            except AttributeError:
                # Sometimes we get an attribute error when running this code.
                # This is sometimes a bug with the website (see 2014,
                # December 30 through 31st), but I think it might also
                # sometimes be a bug with my code. This doesn't happen too
                # often though, so it is a problem for a later time.
                summary = "N/A (Attribute Error)"

            # Creating the first sentence based on the summary
            first_sentence = ""
            if summary:
                first_sentence = nltk.sent_tokenize(summary)[0]
            if first_sentence.count(".") > 1:
                # Nltk doesn't know how to find the first sentence if there
                # isn't a space after the first period, which often happens in
                # this dataset, so I'm accounting for this here.
                if first_sentence.find("report") == -1:
                    # Do nothing, because I'm basing whether this first sentence
                    # is wrong or not based on the chance that there isn't
                    # a space after the reporter, which messes up what is the
                    # end of the first sentence.
                    first_sentence = first_sentence
                elif first_sentence.find(".") < first_sentence.find(
                        "report"):
                    # This means that there's a period which doesn't end a
                    # sentence before the messed up period.
                    report_i = first_sentence.find("report")
                    next_period = first_sentence[report_i:].rfind(".")
                    len1 = len(first_sentence[:report_i])
                    first_sentence = first_sentence[:len1 + next_period + 1]
                else:
                    # The normal case: 'report' comes before the first period,
                    # but then there isn't a space after the the first sentence
                    # ends. This allows me to trim the first sentence so that we
                    # don't get false data.
                    period = first_sentence.find(".")
                    first_sentence = first_sentence[:period + 1]

            # Setting defaults for data not tabulated by the website
            event = "N/A (not found)"
            actor = "N/A (not found)"
            reactor = "N/A (not found)"
            state = "N/A (not found)"
            district = "N/A (not found)"
            village = "N/A (not found)"
            if summary.find("village") == -1:
                village = "none (no mention of 'village')"
            report = "N/A (not found)"
            if summary.find("report") == -1:
                report = "none (no mention of 'report')"
            police_station = "N/A (not found)"
            if summary.find("police") == -1 and \
                    summary.find("Police") == -1:
                police_station = "none (no mention of 'police')"
            forest = "N/A (not found)"
            if first_sentence.find("forest") == -1:
                forest = "None (No mention of 'forest')"

            event_sum = []
            actor_sum = []
            reactor_sum = []
            # Finding the event (killed, set ablaze, explosives, etc)
            if first_sentence.find("killed") != -1:
                event_sum.append("murder")
                actor_sum.append("N/A (unsure)")
                reactor_sum.append("N/A (unsure)")
            if first_sentence.find("ablaze") != -1 or \
                    first_sentence.find("on fire") != -1:
                event_sum.append("set on fire")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("arrested") != -1:
                event_sum.append("arrest")
                actor_sum.append("anti-maoist")
                reactor_sum.append("maoist")
            if first_sentence.find("seized explosives") != -1:
                event_sum.append("seized explosives")
                actor_sum.append("anti-maoist")
                reactor_sum.append("none (passive, no 'victim')")
            if first_sentence.find("shot dead") != -1:
                event_sum.append("murder")
                actor_sum.append("N/A (unsure)")
                reactor_sum.append("N/A (unsure)")
            if first_sentence.find("found dead") != -1:
                event_sum.append("murder")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("shot to death") != -1:
                event_sum.append("murder")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("surrendered") != -1:
                event_sum.append("surrender")
                actor_sum.append("maoist")
                reactor_sum.append("none")
            if first_sentence.find("abducted") != -1:
                if first_sentence.find("released") != -1:
                    event_sum.append("abduction release")
                    actor_sum.append("maoist")
                    reactor_sum.append("anti-maoist")
                else:
                    event_sum.append("abduction")
                    actor_sum.append("maoist")
                    reactor_sum.append("anti-maoist")
            if first_sentence.find("injured") != -1:
                event_sum.append("injury")
                actor_sum.append("N/A (unsure)")
                reactor_sum.append("N/A (unsure)")
            if first_sentence.find("recovered") != -1:
                event_sum.append("recovery")
                actor_sum.append("anti-maoist")
                reactor_sum.append("none (passive, no 'victim')")
            if first_sentence.find("derailed") != -1:
                event_sum.append("derailed train")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("acquitted") != -1:
                event_sum.append("acquittal")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("exchanged fire") != -1 or \
                    first_sentence.find("exchange of fire") != -1:
                event_sum.append("exchange of fire")
                actor_sum.append("both maoist and anti-maoist")
                reactor_sum.append("both maoist and anti-maoist")
            if first_sentence.find(" posters") != -1 or \
                    first_sentence.find("Posters") != -1:
                event_sum.append("Maoist posters")
                actor_sum.append("maoist")
                reactor_sum.append("community")
            if first_sentence.find("threat") != -1:
                event_sum.append("threat")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("explosion") != -1 or \
                    first_sentence.find("blew up") != -1 or \
                    first_sentence.find("blown up") != -1:
                event_sum.append("explosion")
                actor_sum.append("maoist")
                reactor_sum.append("anti-maoist")
            if first_sentence.find("raid") != -1:
                event_sum.append("raid")
                actor_sum.append("anti-maoist")
                reactor_sum.append("maoist")
            if first_sentence.find("found") != -1 and \
                    first_sentence.find("found dead") == -1:
                event_sum.append("find")
                actor_sum.append("anti-maoist")
                reactor_sum.append("none (passive, no 'victim')")
            if first_sentence.find("seized") != -1:
                event_sum.append("contraband seized")
                actor_sum.append("anti-maoist")
                reactor_sum.append("maoist")
            if first_sentence.find("attack") != -1:
                event_sum.append("attack")
                actor_sum.append("N/A (unsure)")
                reactor_sum.append("N/A (unsure)")
            if first_sentence.find("launched") != -1:
                event_sum.append("attack")
                actor_sum.append("anti-maoist")
                reactor_sum.append("maoist")
            if first_sentence.find("died") != -1:
                event_sum.append("death")
                actor_sum.append("maoist")
                reactor_sum.append("none (no 'victim')")
            if first_sentence.find("strike") != -1:
                event_sum.append("strike")
                actor_sum.append("maoist")
                reactor_sum.append("none (no 'victim')")
            statement_list = ["said", "stated", "demanded", "directed",
                              "states"]
            if any(substr in first_sentence for substr in statement_list):
                # When something in this list is in the first sentence, this
                # means that what happened didn't actually happen on that day,
                # so the value of what is said shouldn't be attributed to the
                # date. Instead, what happened on x day was just a speech about
                # X event.
                event = "Statement"
                actor = "N/A (unsure)"
                reactor = "none (passive, no 'victim')"

            if event_sum:
                event = ','.join(event_sum)
            if actor_sum:
                actor = ','.join(actor_sum)
                reactor = ','.join(reactor_sum)
            if event == "N/A (not found)":
                actor = "None (event not found)"
                reactor = "None (event not found)"

            # Finding district & state based on formatting of summaries
            if summary.find(" District of ") != -1 or \
                    summary.find(" District in ") != -1 or \
                    summary.find(" district of ") != -1 or \
                    summary.find(" district in ") != -1:
                # There's a state and district in this summary

                # Setting district index
                dist_i = summary.find(" District of ")
                if dist_i == -1:
                    dist_i = summary.find(" District in ")
                    if dist_i == -1:
                        dist_i = summary.find(" district of ")
                        if dist_i == -1:
                            dist_i = summary.find(" district in ")

                # If the district doesn't come up in the first
                # two sentences, it's probably not relevant.
                if dist_i > second_char(".", summary) != -1:
                    state = "N/A (too long)"
                    district = "N/A (too long)"
                else:
                    i = dist_i - 1
                    j = dist_i + 13
                    # Finding the beginning and end of state & district names
                    while summary[i] != " ":
                        i -= 1
                    while (summary[j] != " ") and (summary[j] != ","):
                        if summary[j] == ".":
                            break
                        if summary[j] == "(":
                            while summary[j] != ")":
                                j += 1
                        else:
                            j += 1

                    district = summary[i+1:dist_i]
                    state = summary[dist_i+13:j]
            elif summary.find(" District on") != -1 or \
                    summary.find(" district on") != -1:
                # There's only a district in this summary, no state values.
                dist_i = summary.find(" District on")
                if dist_i == -1:
                    dist_i = summary.find(" district on")
                i = dist_i - 1

                # If the district doesn't come up in the first
                # two sentences, it's probably not relevant.
                if dist_i > second_char(".", summary) != -1:
                    state = "N/A (too long)"
                    district = "N/A (too long)"
                else:
                    while summary[i] != " ":
                        i -= 1
                    district = summary[i+1:dist_i]
                    state = "N/A (not mentioned)"
            elif summary.find("District") != -1 or \
                    summary.find("district") != -1:
                # Checking for "In _____ District"
                dist_i = summary.find("District")
                if dist_i == -1:
                    dist_i = summary.find("district")

                i = dist_i - 1
                if summary[i] == " ":
                    i -= 1
                space_test = 3  # num of spaces allowed before assumed not valid
                while space_test > 0 and i > 4:
                    if summary[i] == " ":
                        space_test -= 1
                    if summary[i-4:i] == " in ":
                        district = summary[i:dist_i-1]
                        break
                    if summary[i] == ",":
                        # Aka [state], [district]
                        district = summary[i+2:dist_i-1]
                        break
                    if summary[i] == "'":
                        # Aka [state]'s [district]
                        district = summary[i+3:dist_i-1]
                        break
                    i -= 1

            # Cleaning up data
            if district.find("N/A") == -1:
                if len(district) < 3:
                    district = "N/A (too short)"
                elif district[0].islower():
                    district = "N/A (capitalization)"
                if district.find(",") != -1:
                    district = district[district.find(",") + 2:]
                if district.find("Naxal") != -1:
                    # An occasional problem with the data is that it might
                    # contain "Naxal".
                    district = "N/A (contained Naxal)"
            if state[0].islower():
                state = "N/A (capitalization)"

            # If there hasn't been a state identified, it might have just
            # been mentioned by name.
            # This does take a while to run because it needs to search all
            # of these states, so if the researcher looking at this finds
            # this to not provide enough value, they can comment out this code
            # to make the program run faster.
            list_of_indian_states = \
                ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
                 "Chhattisgarh", "Goa", "Gujarat", "Haryana",
                 "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
                 "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
                 "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
                 "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                 "Uttar Pradesh", "Uttarakhand", "West Bengal"]
            if state.find("N/A") != -1:
                for indian_state in list_of_indian_states:
                    if first_sentence.find(indian_state) != -1:
                        state = indian_state
                        break
            # Fixing a bug in the district string finder
            if district.find("village,") != -1:
                index = district.find("village, ")
                district = district[index + 9:]

            if village.find("N/A") != -1 or village.find("none") != -1:
                # There hasn't been a village found, so we're gonna search
                # the first sentence for major cities to see if it was just
                # mentioned randomly, assuming that the reader knew of
                # the city.
                for key in city_dictionary:
                    if first_sentence.find(key) != -1:
                        district = key
                        state = city_dictionary[key]

            # Finding who reported the incident
            if summary.find("reports") != -1:
                report_i = summary.find("reports")
                i = report_i
                while i < len(summary):
                    if summary[i] == ".":
                        break
                    else:
                        i += 1

                # Checking to see if we need to add a .com at the end
                if i + 1 < len(summary):
                    if summary[i+1] == "c":
                        i += 4

                # Sometimes the website forgets spaces, so checking for that
                rep_beg = report_i + 8
                if summary[rep_beg - 1] != " ":
                    rep_beg -= 1
                report = summary[rep_beg:i]

                # Check to see if we're getting a date in the reporting info
                if report.find(" on ") != -1:
                    report = report[:report.find(" on ")]
                else:
                    date_check = date[:4]
                    if report.find(date_check) != -1:
                        report = report[:report.find(date_check)]

                # Final error checking; if it's too long or short,
                # it's probably an error
                if len(report) > 42:
                    report = "N/A (Too long)"
                if len(report) < 4:
                    report = "N/A (Too short)"

            # Finding village
            if summary.find(" village ") != -1 or \
                    summary.find(" village,") != -1:
                village_i = summary.find(" village,")
                if village_i == -1:
                    village_i = summary.find(" village ")
                i = village_i
                while summary[i - 1] != " " and i > 1:
                    i -= 1
                if i == 1:
                    # Error checking to make sure we don't get wraparounds
                    village = "N/A (begins sentence)"
                elif summary[i].islower():
                    # Checking to make sure that this is a proper noun
                    village = "N/A (capitalization)"
                else:
                    village = summary[i:village_i]
            # For additional specification on village
            elif first_sentence.find("villages") != -1:
                village_i = first_sentence.find("villages") - 1
                if first_sentence[village_i] == " ":
                    village_i -= 1
                i = village_i
                while first_sentence[i - 1] != " " and i > 1:
                    i -= 1
                if first_sentence[i - 5:i] != " and ":
                    village = "N/A (didn't find two villages)"
                else:
                    i -= 6
                    while first_sentence[i - 1] != " " and i > 1:
                        i -= 1
                    if i < 0:
                        village = "N/A (begins sentence)"
                    elif first_sentence[i].islower():
                        village = "N/A (capitalization)"
                    else:
                        village = first_sentence[i:village_i + 1]
            elif district.find("N/A") == -1:
                # If we've found a district, sometimes you can find a village
                # because the wording will be [village] in [district]
                village_i = summary.find(district)
                if summary[village_i-4:village_i] == " in ":
                    village_i -= 4  # To roll back away from "in"
                    index = village_i - 1
                    while summary[index] != " ":
                        index -= 1
                    if summary[index+1].isupper() and \
                            summary[village_i-1] != ",":
                        # Sometimes we catch commas, and this means it isn't
                        # correct, so make sure that there's no comma at the end
                        if len(summary[index+1:village_i]) > 3 and \
                                summary[index+1:village_i] != "Station" and \
                                summary[index+1:village_i] != "Inspector":
                            # Sometimes we just get acronyms, so remove those
                            # Sometimes we get general words, so remove those.
                            village = summary[index+1:village_i]
                elif summary[village_i-2] == ",":
                    # Sometimes it's [village], [district]
                    village_i -= 2
                    index = village_i
                    while summary[index] != " ":
                        index -= 1
                    if summary[index+1].isupper():
                        village = summary[index+1:village_i]

            elif first_sentence.find("area") != -1:
                # Sometimes, instead of village, the word 'area' is used.
                # This needs additional care for searching though because it is
                # a common word.
                area_i = first_sentence.find("area") - 1
                if first_sentence[area_i] == " ":
                    area_i -= 1
                i = area_i
                while first_sentence[i - 1] != " " and i > 1:
                    i -= 1
                if i == 1:
                    village = "N/A (begins sentence for area)"
                elif first_sentence[i].islower():
                    village = "N/A (capitalization for area)"
                else:
                    if first_sentence[area_i + 1] == " ":
                        area_i += 1  # Spacing check for village
                    village = first_sentence[i:area_i]
                    village += " area"
                if village == "area":
                    village = "N/A (area mistake)"

            # Finding police station under which this event happened.
            if summary.find("Police Station") != -1:
                police_i = summary.find("Police Station") - 1
                if summary[police_i] == " ":  # Checking for spacing
                    police_i -= 1
                i = police_i
                while summary[i - 1] != " " and i > 1:
                    i -= 1
                if i == 1:
                    # Error checking to make sure we don't get wraparounds
                    police_station = "N/A (begins sentence)"
                elif summary[i].islower():
                    # Checking to make sure that this is a proper noun
                    police_station = "N/A (capitalization)"
                else:
                    while summary[police_i] != " ":
                        police_i += 1
                    police_station = summary[i:police_i]
                    police_station += " Police Station"
            elif first_sentence.find("Police") != -1 or \
                    first_sentence.find("police") != -1:
                police_i = first_sentence.find("Police") - 1
                if first_sentence[police_i] == " ":
                    police_i -= 1  # Checking for spacing at beginning
                i = police_i
                while first_sentence[i - 1] != " " and i > 1:
                    i -= 1
                if i < 0:
                    police_station = "N/A (began sentence)"
                elif first_sentence[i].islower():
                    # Checking to make sure this is a proper noun
                    police_station = "N/A (capitalization)"
                else:
                    police_station = first_sentence[i:police_i+1]
                    substr_list = ["Distr", "Reserv", "Borde", "City",
                                   "Railway", "Armed", "Senior", "Auxiliary",
                                   "State", "Polic", "Rural"]
                    if any(substr in police_station for substr in substr_list) \
                            or "Police" in police_station or \
                            len(police_station) < 3:
                        # Checking to make sure the type of police is giving
                        # the location and not just a general police
                        # These aren't fully spelled because there are often
                        # typos in here, so I want to catch all wrong police.
                        police_station = "N/A (location not found)"
                    else:
                        police_station = police_station + " Police"

            # Finding possible forest where this occurred
            if first_sentence.find("forest of") != -1:
                forest_i = first_sentence.find("forest of") + 9  # To next word
                if first_sentence[forest_i] == " ":  # Spacing check
                    forest_i += 1
                i = forest_i
                if first_sentence[i].islower():
                    # Checking to make sure this is a proper noun
                    forest = "N/A (capitalization)"
                else:
                    while first_sentence[i] != " " and first_sentence[i] != ".":
                        i += 1
                    forest = first_sentence[forest_i:i]
            elif first_sentence.find("forest") != -1:
                forest_i = first_sentence.find("forest")
                i = forest_i - 2
                while first_sentence[i - 1] != " " and i > 1:
                    i -= 1
                if i == 1:
                    # Error checking to make sure we don't get wraparounds
                    forest = "N/A (begins sentence)"
                elif first_sentence[i].islower():
                    # Checking to make sure this is a proper noun
                    forest = "N/A (capitalization)"
                else:
                    if first_sentence[forest_i - 1] == " ":
                        forest_i -= 1  # Checking for bad formatting
                    forest = first_sentence[i:forest_i]

            # Appending each value to its corresponding list
            date_list.append(date)
            event_list.append(event)
            actor_list.append(actor)
            reactor_list.append(reactor)
            state_list.append(state)
            district_list.append(district)
            village_list.append(village)
            police_station_list.append(police_station)
            forest_list.append(forest)
            report_list.append(report)
            summary_list.append(summary)

cols = list(zip(date_list, event_list, actor_list, reactor_list,
                state_list, district_list, village_list, police_station_list,
                forest_list, report_list, summary_list))

# Create the data frame and save it.
df = pd.DataFrame(cols, columns=['Date', 'Event', 'Actor',
                                 'Reactor',
                                 'State', 'District', 'Village',
                                 'Police Area', 'Forest', 'Reported By',
                                 'Summary'])

# Summing up N/As in each column to keep track of how accurate this is
date_na = sum(df['Date'].str.count('N/A'))
event_na = sum(df['Event'].str.count('N/A'))
committed_na = sum(df['Actor'].str.count('N/A'))
received_na = sum(df['Reactor'].
                  str.count('N/A'))
state_na = sum(df['State'].str.count('N/A'))
district_na = sum(df['District'].str.count('N/A'))
village_na = sum(df['Village'].str.count('N/A'))
police_station_na = sum(df['Police Area'].str.count('N/A'))
forest_na = sum(df['Forest'].str.count('N/A'))
reported_na = sum(df['Reported By'].str.count('N/A'))
summary_na = sum(df['Summary'].str.count('N/A'))
# Putting N/A summations into their respective cells
new_row = {'Date': date_na, 'Event': event_na,
           'Actor': committed_na,
           'Reactor': received_na,
           'State': state_na, 'District': district_na, 'Village': village_na,
           'Police Area': police_station_na, 'Forest': forest_na,
           'Reported By': reported_na, 'Summary': summary_na}
df = df.append(new_row, ignore_index=True)

# Putting all this into a csv
df.to_csv('indian_maoist_insurgency/Violence_info_one_year.csv')
