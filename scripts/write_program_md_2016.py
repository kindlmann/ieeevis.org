#!/usr/bin/env python

"""
Write program to MD from the Google Spreadsheet.

Carlos Scheidegger, Sam Gratzl, Lane Harrison, 2016-2017

We recommend you use this under a virtual environment. Create
a virtualenv and then install the required libraries with

$ pip install -r requirements.txt

If you need to run this locally, please contact Sam or Carlos for
the private key to access the spreadsheet from the script.

"""

from data import *

import min_html as h
import sys

gc = get_spreadsheet("VIS2016 Program")
records = load_sheet_by_name(gc, "Program").get_all_records()
sessions = load_sheet_by_name(gc, "Sessions").get_all_records()
awards = dict((award["paper-id"], award) for award in load_sheet_by_name(gc, "Awards").get_all_records())
session_dict = dict((session["Name"], session) for session in sessions)

def guess_venue(session):
    ids = set([paper["ID"][:paper["ID"].find('-')] for paper in session["Value"]
           if (not paper["ID"].upper().startswith("TVCG"))])
    if len(ids) > 1 and list(ids)[0].startswith("CG&A"):
            return "cga" 
    if len(ids) <> 1 and session["Key"].startswith("VIS Awards"):
        return "all"
    if len(ids) <> 1:
        sys.stderr.write("couldn't guess conference for session %s" % session["Key"])
        # return None
        # raise Exception("couldn't guess conference for session %s" % session["Key"])
    return list(ids)[0]

venue_name = { "cga": "CG&A",
               "infovis": "InfoVis",
               "scivis": "SciVis",
               "all": "VIS",
               "vast": "VAST" }

def paper_type(paper):
    t = paper["Type"]
    if t == "AJ":
        return " (J)"
    if t == "AC":
        return " (C)"
    if t == "TVCG":
        return " (T)"
    if paper["ID"].startswith("TVCG"):
        return " (T)"
    if paper["ID"].startswith("cga"):
        return ""
    return " (J)"

def award_string(award):
    if award is None:
        return ""
    if award["type"] == 'Honorable Mention':
        return " *(Best Paper Honorable Mention)*"
    if award["type"] == 'Award vast':
        return " *(Best Paper Award, VAST)*"
    if award["type"] == 'Award infovis':
        return " *(Best Paper Award, InfoVis)*"
    if award["type"] == 'Award scivis':
        return " *(Best Paper Award, SciVis)*"
    raise Exception("Could not recognize award type '%s'" % award["type"])

def render_session(session, out):
    name = session["Key"]
    venue = venue_name[guess_venue(session)]
    out.write("**%s**  \n" % session_dict[name]["Day"].upper())
    out.write("**%s**  \n" % session_dict[name]["Time"])
    out.write("**Room: %s**  \n" % session_dict[name]["Room"])
    if venue is not None:
        out.write("*%s: %s*  \n" % (venue, name))
    else:
        out.write("*%s  \n" % name)
    out.write("*Session Chair: %s*  \n" % (session_dict[name]["Chair"]).encode("utf-8"))
    out.write("\n")
    for paper in session["Value"]:
        award = awards.get(paper["ID"], None)
        out.write(("**%s%s**%s  \n" % (paper["Title"], paper_type(paper), award_string(award))).encode("utf-8"))
        out.write(("Authors: %s  \n" % paper["Author list"]).encode("utf-8"))
        out.write(("[Video Preview](%s)\n" % paper["FF Video"]).encode("utf-8"))
        if paper["DOI"] != "":
            out.write(("| [DOI](%s)\n" % paper["DOI"]).encode("utf-8"))
        out.write("\n")
    out.write("<hr/>\n\n")


def session_key(session):
    order = {
        "8": 0,
        "10": 1,
        "2": 2,
        "4": 3,
        }
    venue_order = {
        "VIS": 0,
        "VAST": 1,
        "InfoVis": 2,
        "SciVis": 3,
        "CG&A": 4,
        }
    name = session["Key"]
    venue = venue_order[venue_name[guess_venue(session)]]
    metadata = session_dict[name]
    day = metadata["Day"][-1:]
    time = order[metadata["Time"][:metadata["Time"].find(':')]]
    return (day, time, venue)

out = sys.stdout
for session in sorted(group_by(records, lambda k: k['Session']), key = session_key):
    render_session(session, out)
