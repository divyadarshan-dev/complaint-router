"""
evaluate.py - measure how accurate the router is. Run with: python evaluate.py

Includes 55 realistic campus complaints in English, Hinglish, and romanised Punjabi,
including spelling typos, LPU-style hostel/block formats, missing room numbers,
and ambiguous/multi-issue complaints that should trigger "Human Review".
"""
import time
from router import route_complaint

# (complaint, expected_queue)
# expected_queue is either one of the 6 departments OR "Human Review"
TESTS = [
    # --- Plumbing (8) ---
    ("bhai 4th floor ka washroom ka tap 3 din se leak kar rha h", "Plumbing"),
    ("geyser se paani nahi aa rha room 305 block C", "Plumbing"),
    ("washroom ka flush kharab h 2nd floor block A", "Plumbing"),
    ("BH-4 3rd floor washroom drain block ho gaya hai paani bhar rha hai", "Plumbing"),
    ("bathroom di tooti tut gayi hai room 112 ch", "Plumbing"),
    ("water cooler leaking badly near staircase ground floor", "Plumbing"),
    ("shower ka pressure bilkul zero hai subah se", "Plumbing"),
    ("sink pipe se ganda paani aa rha hai GH-2 1st floor", "Plumbing"),

    # --- Electrical (8) ---
    ("room 212 ka fan kaam nahi kar raha, bahut garmi h", "Electrical"),
    ("tubelight fuse ho gayi corridor ch, 3rd floor", "Electrical"),
    ("switch board se spark aa rahi hai room 118", "Electrical"),
    ("bijli chali gayi hai sirf hamare wing mein BH-2", "Electrical"),
    ("AC cooling nahi kar rha aur awaz kar rha hai room 404", "Electrical"),
    ("charging socket jal gaya hai bed ke paas wala", "Electrical"),
    ("pankha bahut slow ghoom rha hai condenser kharab lagta h", "Electrical"),
    ("light flickr kr rhi h bar bar study table ki", "Electrical"),

    # --- Wi-Fi (8) ---
    ("wifi bohot slow chal rha hai block B mein", "Wi-Fi"),
    ("router band pea hai, internet nahi chal reha", "Wi-Fi"),
    ("my wifi keeps disconnecting every 10 minutes in room 410", "Wi-Fi"),
    ("24online login page open nahi ho rha hostel mein", "Wi-Fi"),
    ("lan port kaam nahi kar rha room 209 BH-5", "Wi-Fi"),
    ("net bilkul dead hai 5th floor pe kal raat se", "Wi-Fi"),
    ("wifi connect ho rha h par no internet dikha rha h", "Wi-Fi"),
    ("hotspot bhi nahi chal rha aur hostel router red light blink kr rha h", "Wi-Fi"),

    # --- Mess (8) ---
    ("mess ka khana bahut kharab tha aaj, dal mein keede the", "Mess"),
    ("mess ch roti kachi si, paani vi nahi si", "Mess"),
    ("breakfast mein cold milk aur stale bread de rahe hain BH-3 mess", "Mess"),
    ("plates properly wash nahi hoti dining hall mein", "Mess"),
    ("mess timing 9 baje tak rakho raat ko, 8:30 pe band kar dete hain", "Mess"),
    ("aaj dinner mein paneer bilkul khatam ho gaya 8 baje hi", "Mess"),
    ("mess staff badtameezi se baat karta hai jab extra chapati mango", "Mess"),
    ("drinking water filter in mess tastes weird", "Mess"),

    # --- Academic (8) ---
    ("sir ne timetable change kiya par notice nahi aaya, class miss ho gayi", "Academic"),
    ("attendance galat lagi hai mera, DBMS di class di", "Academic"),
    ("internal marks portal pe update nahi hue", "Academic"),
    ("UMS pe backlog exam form submit nahi ho rha", "Academic"),
    ("section change ki request pending hai 2 hafte se HOD office mein", "Academic"),
    ("projector nahi chal rha Block 34 room 204 mein lecture ruk gaya", "Academic"),
    ("makeup class ka room number galat show ho rha hai portal pe", "Academic"),
    ("lab evaluation dates clash kar rhi hain mid term se", "Academic"),

    # --- Other (7) ---
    ("hostel gate pe guard rude behave kar raha tha", "Other"),
    ("corridor mein bahut kachra pada hai safai nahi hui 2 din se", "Other"),
    ("room 310 ke bagal wale raat 2 baje tak loud music bajate hain", "Other"),
    ("stray dogs hostel entrance pe aa jate hain raat ko dar lagta hai", "Other"),
    ("mera parcel main gate pe guard ne kho diya", "Other"),
    ("almirah ka lock toot gaya hai carpenter bhej do room 105", "Other"),
    ("laundry wale ne meri white shirt kharab kar di", "Other"),

    # --- Human Review / Tricky Edge Cases (8) ---
    ("bhai bohot dikkat ho rhi hai room mein jaldi kuch karo", "Human Review"),
    ("fan bhi band hai aur washroom ka tap bhi leak kar rha hai", "Human Review"),
    ("paani aur bijli dono nahi aa rhi subah se", "Human Review"),
    ("asdfghjkl kuch samajh nahi aa rha", "Human Review"),
    ("mess aur wifi dono bekar hain is hostel ke", "Human Review"),
    ("sir please check karo mera issue abhi tak solve nahi hua", "Human Review"),
    ("warden se baat karni hai urgent matter hai", "Human Review"),
    ("portal pe login nahi ho rha", "Human Review"),
]

correct = 0
human_review_hits = 0
human_review_total = sum(1 for _, exp in TESTS if exp == "Human Review")
total_latency = 0.0
total_cost = 0.0

for complaint, expected in TESTS:
    ticket = route_complaint(complaint)
    got_queue = ticket["queue"]
    ok = got_queue == expected
    correct += ok
    if expected == "Human Review" and ok:
        human_review_hits += 1
    total_latency += ticket["latency_s"]
    total_cost += ticket["cost_usd"]
    print("%s  expected=%-12s got=%-12s conf=%.2f urg=%-6s loc=%s/%s/%s | %s" % (
        "OK  " if ok else "FAIL",
        expected,
        got_queue,
        ticket["confidence"],
        ticket["urgency"],
        ticket["block"],
        ticket["floor"],
        ticket["room"],
        complaint,
    ))
time.sleep(2.5)
n = len(TESTS)
print()
print("Overall Queue Accuracy : %d/%d = %.1f%%" % (correct, n, 100 * correct / n))
print("Human Review Catch Rate: %d/%d = %.1f%%" % (human_review_hits, human_review_total, 100 * human_review_hits / human_review_total))
print("Avg latency            : %.2f s" % (total_latency / n))
print("Avg cost per complaint : $%.5f" % (total_cost / n))
