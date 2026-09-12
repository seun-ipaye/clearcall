"""
Generates the ClearCall mock call dataset: 200 realistic contact-center
call records (with multi-turn transcripts) for a Canadian health & dental
benefits call center.

Deliberately weights the random generation so the storylines the dashboard
is meant to surface actually show up in the data:
  - Entente drives a disproportionate share of web-portal ("web help") calls
  - Escalations skew toward GreenShield and Entente
  - Claim denials, complaints, and out-of-country claims escalate most often

LLM-derived fields (sentiment_score, complexity_score, escalation_risk_flag)
are left as null placeholders here — they get populated by the separate
Claude-powered analytics pipeline that reads this file.

Usage:
    python backend/scripts/generate_dataset.py
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
random.seed(SEED)
fake = Faker("en_CA")
Faker.seed(SEED)

NUM_RECORDS = 200
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "calls.json"

CLIENTS = ["GreenShield", "RBC Insurance", "Wawanesa", "Victor Insurance", "Entente"]
BASE_CLIENT_WEIGHTS = {
    "GreenShield": 0.30,
    "RBC Insurance": 0.20,
    "Wawanesa": 0.15,
    "Victor Insurance": 0.15,
    "Entente": 0.20,
}
WEB_HELP_CLIENT_WEIGHTS = {
    "GreenShield": 0.15,
    "RBC Insurance": 0.15,
    "Wawanesa": 0.10,
    "Victor Insurance": 0.10,
    "Entente": 0.50,
}
ESCALATION_CLIENT_MULTIPLIER = {
    "GreenShield": 1.4,
    "Entente": 1.3,
    "RBC Insurance": 0.8,
    "Wawanesa": 0.8,
    "Victor Insurance": 0.85,
}

PROVINCES = ["ON", "QC", "BC", "AB", "MB", "SK", "NS", "NB", "NL", "PE", "YT", "NT", "NU"]
PROVINCE_WEIGHTS = [0.36, 0.20, 0.15, 0.11, 0.04, 0.03, 0.03, 0.03, 0.02, 0.01, 0.007, 0.007, 0.006]

AGENT_IDS = [f"AGT-{i:02d}" for i in range(1, 17)]
AGENT_ALIASES = {aid: fake.first_name() for aid in AGENT_IDS}
AGENT_WEIGHTS = [round(random.uniform(0.7, 1.4), 2) for _ in AGENT_IDS]

# ---------------------------------------------------------------------------
# Call reason taxonomy
# ---------------------------------------------------------------------------
# category groups: claim_inquiry, benefit_inquiry, claim_status, web_help,
# transfer, preauth, admin, complaint
REASONS = [
    {"id": "claim_denial", "name": "Claim inquiry - denial reason", "category": "claim_inquiry",
     "caller_type": "member", "weight": 14, "escalation": 0.35, "duration": (240, 540)},
    {"id": "claim_general", "name": "Claim inquiry - general/coverage question", "category": "claim_inquiry",
     "caller_type": "member", "weight": 10, "escalation": 0.10, "duration": (120, 300)},
    {"id": "benefit_balance", "name": "Benefit inquiry - remaining balance", "category": "benefit_inquiry",
     "caller_type": "member", "weight": 12, "escalation": 0.05, "duration": (90, 240)},
    {"id": "benefit_coverage", "name": "Benefit inquiry - coverage details", "category": "benefit_inquiry",
     "caller_type": "member", "weight": 10, "escalation": 0.08, "duration": (120, 300)},
    {"id": "benefit_eligibility", "name": "Benefit inquiry - eligibility/waiting period", "category": "benefit_inquiry",
     "caller_type": "member", "weight": 6, "escalation": 0.10, "duration": (150, 320)},
    {"id": "claim_status_submitted", "name": "Claim status - submitted claim", "category": "claim_status",
     "caller_type": "member", "weight": 10, "escalation": 0.08, "duration": (100, 260)},
    {"id": "claim_status_payment", "name": "Claim status - payment/EFT issued", "category": "claim_status",
     "caller_type": "member", "weight": 6, "escalation": 0.05, "duration": (90, 220)},
    {"id": "web_login", "name": "Web portal - login/access issue", "category": "web_help",
     "caller_type": "provider", "weight": 8, "escalation": 0.15, "duration": (180, 420)},
    {"id": "web_submission", "name": "Web portal - claim submission help", "category": "web_help",
     "caller_type": "provider", "weight": 8, "escalation": 0.12, "duration": (200, 480)},
    {"id": "web_registration", "name": "Web portal - registration/setup", "category": "web_help",
     "caller_type": "provider", "weight": 4, "escalation": 0.10, "duration": (240, 500)},
    {"id": "web_navigation", "name": "Web portal - navigation/how-to", "category": "web_help",
     "caller_type": "provider", "weight": 4, "escalation": 0.05, "duration": (120, 300)},
    {"id": "transfer_billing", "name": "Transfer - billing department", "category": "transfer",
     "caller_type": "mixed", "weight": 5, "escalation": 0.05, "duration": (60, 180)},
    {"id": "transfer_dental", "name": "Transfer - dental consultant team", "category": "transfer",
     "caller_type": "mixed", "weight": 4, "escalation": 0.05, "duration": (60, 180)},
    {"id": "transfer_provider_relations", "name": "Transfer - provider relations", "category": "transfer",
     "caller_type": "provider", "weight": 3, "escalation": 0.05, "duration": (60, 180)},
    {"id": "transfer_complaints", "name": "Transfer - complaints/escalations team", "category": "transfer",
     "caller_type": "mixed", "weight": 3, "escalation": 0.20, "duration": (90, 240)},
    {"id": "preauth_general", "name": "Predetermination/pre-authorization request", "category": "preauth",
     "caller_type": "member", "weight": 6, "escalation": 0.15, "duration": (200, 420)},
    {"id": "preauth_ortho", "name": "Orthodontic pre-authorization", "category": "preauth",
     "caller_type": "member", "weight": 4, "escalation": 0.18, "duration": (220, 450)},
    {"id": "cob_inquiry", "name": "Coordination of benefits (COB) inquiry", "category": "benefit_inquiry",
     "caller_type": "member", "weight": 5, "escalation": 0.12, "duration": (180, 360)},
    {"id": "direct_deposit", "name": "Direct deposit / EFT setup", "category": "admin",
     "caller_type": "mixed", "weight": 4, "escalation": 0.05, "duration": (120, 240)},
    {"id": "address_update", "name": "Address or contact info update", "category": "admin",
     "caller_type": "member", "weight": 4, "escalation": 0.02, "duration": (60, 150)},
    {"id": "password_reset", "name": "Web portal - password reset", "category": "web_help",
     "caller_type": "provider", "weight": 4, "escalation": 0.03, "duration": (60, 150)},
    {"id": "eob_request", "name": "Explanation of benefits (EOB) request", "category": "admin",
     "caller_type": "member", "weight": 4, "escalation": 0.05, "duration": (90, 200)},
    {"id": "missing_cheque", "name": "Missing or lost cheque inquiry", "category": "claim_status",
     "caller_type": "member", "weight": 3, "escalation": 0.20, "duration": (150, 320)},
    {"id": "fax_confirmation", "name": "Fax/document submission confirmation", "category": "admin",
     "caller_type": "provider", "weight": 3, "escalation": 0.05, "duration": (60, 150)},
    {"id": "email_followup", "name": "Email correspondence follow-up", "category": "admin",
     "caller_type": "mixed", "weight": 3, "escalation": 0.10, "duration": (90, 220)},
    {"id": "provider_enrollment", "name": "Provider enrollment inquiry", "category": "admin",
     "caller_type": "provider", "weight": 3, "escalation": 0.08, "duration": (180, 360)},
    {"id": "claim_resubmission", "name": "Claim resubmission assistance", "category": "claim_inquiry",
     "caller_type": "provider", "weight": 4, "escalation": 0.15, "duration": (200, 400)},
    {"id": "out_of_country", "name": "Out-of-country claim inquiry", "category": "claim_inquiry",
     "caller_type": "member", "weight": 2, "escalation": 0.25, "duration": (240, 480)},
    {"id": "plan_documents", "name": "Plan document/booklet request", "category": "admin",
     "caller_type": "member", "weight": 2, "escalation": 0.02, "duration": (60, 150)},
    {"id": "general_complaint", "name": "General complaint", "category": "complaint",
     "caller_type": "mixed", "weight": 3, "escalation": 0.40, "duration": (200, 450)},
]

DENIAL_REASONS = [
    "the annual maximum for that benefit had already been reached",
    "there was no predetermination on file before the service was provided",
    "the service isn't covered under the plan's fee guide",
    "the claim was submitted after the 90-day filing deadline",
    "the dependent wasn't listed as eligible on the plan at the time of service",
    "the frequency limit for that procedure hadn't been met yet (too soon since the last one)",
    "the provider's billed code didn't match what was authorized",
    "coordination of benefits with the spouse's plan hadn't been completed",
]

SERVICES = [
    "a dental cleaning and exam", "a filling", "a root canal", "a crown", "orthodontic adjustments",
    "a physiotherapy session", "a pair of orthotics", "an eye exam", "prescription glasses",
    "a massage therapy session", "a scaling and root planing procedure", "a dental extraction",
]

PORTAL_ERRORS = [
    "an 'invalid session' error", "a blank white screen after login", "a 'claim already submitted' error",
    "the page just spinning and never loading", "an error saying their provider number wasn't recognized",
    "a timeout message halfway through the claim form",
]

COORDINATORS = ["Priya", "Marcus", "Devon", "Aisha", "Jordan", "our Dental Coordinator", "our Claims Team Lead"]


def weighted_choice(rng, options, weights):
    return rng.choices(options, weights=weights, k=1)[0]


def pick_client(rng, reason):
    weights = WEB_HELP_CLIENT_WEIGHTS if reason["category"] == "web_help" else BASE_CLIENT_WEIGHTS
    return weighted_choice(rng, CLIENTS, [weights[c] for c in CLIENTS])


def resolve_caller_type(rng, reason):
    if reason["caller_type"] == "mixed":
        return "plan_member" if rng.random() < 0.55 else "provider"
    return "plan_member" if reason["caller_type"] == "member" else "provider"


def clamp(value, low, high):
    return max(low, min(high, value))


def money(rng, low=25, high=1800):
    return round(rng.uniform(low, high), 2)


def member_id(rng):
    return f"{rng.randint(100000, 999999)}-{rng.randint(0, 9)}"


def provider_id(rng):
    return f"P{rng.randint(10000, 99999)}"


def random_business_datetime(rng, start, end):
    delta_days = (end - start).days
    day = start + timedelta(days=rng.randint(0, delta_days))
    weekday = day.weekday()  # 0=Mon .. 6=Sun
    if weekday == 6:
        day -= timedelta(days=2)  # nudge Sundays to Friday, call center is closed
    elif weekday == 5 and rng.random() > 0.15:
        day -= timedelta(days=1)  # light Saturday coverage only
    if day.weekday() == 5:
        hour = rng.choice([9, 10, 11, 12, 13, 14])
    else:
        hour = weighted_choice(rng, list(range(8, 18)),
                                [3, 5, 7, 8, 9, 9, 8, 8, 7, 6])
    minute = rng.randint(0, 59)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ---------------------------------------------------------------------------
# Transcript building blocks
# ---------------------------------------------------------------------------

def opening_turns(rng, ctx):
    agent_name = AGENT_ALIASES[ctx["agent_id"]]
    caller_name = ctx["caller_name"]
    greeting = rng.choice([
        f"Thank you for calling {ctx['client']} Benefits, this is {agent_name} speaking, how can I help you today?",
        f"{ctx['client']} Benefits, this is {agent_name}, how may I assist you?",
        f"Good {ctx['daypart']}, thanks for calling {ctx['client']}, my name's {agent_name} — what can I help with today?",
    ])
    turns = [("Agent", greeting)]
    if ctx["caller_type"] == "plan_member":
        turns.append(("Caller", f"Hi, it's {caller_name} calling. {ctx['intro_line']}"))
        turns.append(("Agent", "No problem, I can help with that. Can I get your member ID or date of birth to pull up the file?"))
        turns.append(("Caller", f"Sure, it's {member_id(rng)}."))
        turns.append(("Agent", "Perfect, thank you, I have your file open now."))
    else:
        turns.append(("Caller", f"Hi, this is {caller_name} calling from {ctx['provider_name']}. {ctx['intro_line']}"))
        turns.append(("Agent", "Sure thing, can I get your provider number to look into that?"))
        turns.append(("Caller", f"Yep, it's {provider_id(rng)}."))
        turns.append(("Agent", "Great, I've got you pulled up."))
    return turns


def closing_turns(rng, ctx):
    if ctx["resolution_status"] == "resolved":
        agent_line = rng.choice([
            "Glad I could sort that out for you. Is there anything else I can help with today?",
            "That should take care of it. Anything else on the file I can help with?",
        ])
        caller_line = rng.choice(["No, that's everything, thank you!", "Nope, that's all I needed, thanks so much."])
        agent_close = rng.choice([
            "You're very welcome, have a great rest of your day.",
            "My pleasure, take care now.",
        ])
        return [("Agent", agent_line), ("Caller", caller_line), ("Agent", agent_close)]
    if ctx["resolution_status"] == "transferred":
        return [
            ("Agent", "I'm going to transfer you over to the team that handles this specifically so they can take it from here, is that alright?"),
            ("Caller", "Okay, sure, thank you."),
            ("Agent", "Perfect, one moment while I connect you."),
        ]
    return [
        ("Agent", "I know that's not the answer you were hoping for. I've made detailed notes on the file so the next step is clear."),
        ("Caller", ctx["frustration_line"]),
        ("Agent", "I completely understand the frustration — I've flagged it appropriately and included everything discussed today."),
    ]


def escalation_turns(rng, ctx):
    coordinator = rng.choice(COORDINATORS)
    turns = [
        ("Agent", f"This needs a second look — would it be alright if I put you on a brief hold while I check with {coordinator}?"),
        ("Caller", "Yeah, that's fine, go ahead."),
        ("Agent", "Thanks for your patience, back in just a moment."),
        ("Agent", f"Thanks for holding. I spoke with {coordinator} and here's where things stand."),
    ]
    if ctx["resolution_status"] == "resolved":
        turns.append(("Agent", rng.choice([
            f"{coordinator[0].upper()}{coordinator[1:]} agreed this qualifies for an exception, so I'm able to get this resolved for you today.",
            f"Good news — {coordinator} approved this, so we're all set.",
        ])))
    elif ctx["resolution_status"] == "transferred":
        turns.append(("Agent", f"{coordinator[0].upper()}{coordinator[1:]} felt this needs a closer look from a specialist team, so I'll transfer you over there now."))
    else:
        turns.append(("Agent", f"Unfortunately {coordinator} confirmed the original decision stands based on the plan rules."))
    return turns


def build_body(reason_id, rng, ctx):
    builder = BODY_BUILDERS[reason_id]
    return builder(rng, ctx)


def body_claim_denial(rng, ctx):
    service = rng.choice(SERVICES)
    denial = rng.choice(DENIAL_REASONS)
    amount = money(rng)
    turns = [
        ("Caller", f"I'm calling about a claim that got denied for {service}, I don't understand why."),
        ("Agent", f"Let me pull that up... okay, I see the claim for ${amount:.2f}. It looks like it was denied because {denial}."),
        ("Caller", "That doesn't seem right, nobody told me that beforehand."),
    ]
    if not ctx["escalated"]:
        turns.append(("Agent", "I've double-checked the plan rules and unfortunately the denial is correct based on the terms of the plan."))
    return turns


def body_claim_general(rng, ctx):
    service = rng.choice(SERVICES)
    return [
        ("Caller", f"I had {service} done and just wanted to check what my plan covers for that."),
        ("Agent", "Sure, let me look at your coverage details for that category."),
        ("Agent", f"You're covered at {rng.choice([50,60,70,80,100])}% for that, up to the annual maximum on your plan."),
        ("Caller", "Okay great, that's helpful, thank you."),
    ]


def body_benefit_balance(rng, ctx):
    category = rng.choice(["dental", "paramedical", "vision", "orthodontic"])
    remaining = money(rng, 0, 2000)
    used = money(rng, 0, 1500)
    return [
        ("Caller", f"Can you tell me how much I have left on my {category} benefits this year?"),
        ("Agent", f"Of course, one moment. You've used ${used:.2f} so far, and you have ${remaining:.2f} remaining for this benefit year."),
        ("Caller", "Perfect, that's exactly what I needed to know."),
    ]


def body_benefit_coverage(rng, ctx):
    service = rng.choice(SERVICES)
    return [
        ("Caller", f"Before I book an appointment, I wanted to check if {service} is covered under my plan."),
        ("Agent", "Happy to check that for you. Let me look at your plan's fee guide."),
        ("Agent", rng.choice([
            f"Yes, that's covered at {rng.choice([50,60,80])}%, as long as it's within your frequency limit.",
            "That one actually isn't covered under your current plan, unfortunately.",
        ])),
        ("Caller", "Okay, good to know before I go in."),
    ]


def body_benefit_eligibility(rng, ctx):
    return [
        ("Caller", "I just started this job and I'm not sure if my benefits have kicked in yet."),
        ("Agent", "Let me check your enrollment date. Most plans have a 3-month waiting period from your hire date."),
        ("Agent", rng.choice([
            "Good news, your waiting period ended last month, so you're fully eligible now.",
            "It looks like you still have a few weeks left in your waiting period before coverage begins.",
        ])),
        ("Caller", "Ah okay, that explains it, thanks for checking."),
    ]


def body_claim_status_submitted(rng, ctx):
    days_ago = rng.randint(3, 21)
    return [
        ("Caller", f"I submitted a claim about {days_ago} days ago and haven't heard anything back."),
        ("Agent", "Let me check the status of that for you."),
        ("Agent", rng.choice([
            "I see it's still in processing, it should finalize within the next few business days.",
            "It looks like that one actually finished processing yesterday and payment was issued.",
            "I don't see that claim on file yet — it may not have made it through, let's resubmit it.",
        ])),
        ("Caller", "Okay, thanks for checking on that for me."),
    ]


def body_claim_status_payment(rng, ctx):
    amount = money(rng)
    return [
        ("Caller", "I'm just calling to confirm a payment went through for a claim I submitted."),
        ("Agent", f"Let me look... yes, I can confirm a payment of ${amount:.2f} was issued."),
        ("Caller", "Great, I just wanted to make sure, thank you."),
    ]


def body_web_login(rng, ctx):
    error = rng.choice(PORTAL_ERRORS)
    return [
        ("Caller", f"I'm trying to log into the provider portal and I keep getting {error}."),
        ("Agent", "Sorry about that, let's get it sorted. Can you try clearing your browser cache and logging in again?"),
        ("Caller", "I tried that already, still no luck."),
        ("Agent", "Okay, let me check on our end if there's an account lockout or a system issue."),
    ]


def body_web_submission(rng, ctx):
    return [
        ("Caller", "I'm trying to submit a claim through the portal but the form won't let me proceed to the next step."),
        ("Agent", "Let's walk through it together — which field are you on right now?"),
        ("Caller", "The procedure code field, it keeps saying invalid code."),
        ("Agent", rng.choice([
            "Ah, that code was updated recently — try the new five-digit version instead of the old one.",
            "That field actually needs the code without the letter prefix, let's try that.",
        ])),
    ]


def body_web_registration(rng, ctx):
    return [
        ("Caller", "We're a new clinic and trying to get registered on the provider portal."),
        ("Agent", "Welcome aboard! I can walk you through registration. Do you have your provider number handy?"),
        ("Caller", "Yes, I have it right here."),
        ("Agent", "Great, let's go through the setup steps together."),
    ]


def body_web_navigation(rng, ctx):
    return [
        ("Caller", "I'm on the portal but I can't figure out where to view past claim submissions."),
        ("Agent", "No problem, that's under the 'Claims History' tab on the left-hand menu."),
        ("Caller", "Oh I see it now, thank you, that was hiding on me."),
    ]


def body_password_reset(rng, ctx):
    return [
        ("Caller", "I'm locked out of my portal account, can you help me reset my password?"),
        ("Agent", "Sure, I'll send a reset link to the email on file — can you confirm that email for me?"),
        ("Caller", "Yes, it's the clinic's main email."),
        ("Agent", "Perfect, that's sent, you should have it within a few minutes."),
    ]


def body_transfer_billing(rng, ctx):
    return [
        ("Caller", "I actually have a billing question, I think I need someone else for this."),
        ("Agent", "No problem, that would be our billing team, let me connect you over."),
    ]


def body_transfer_dental(rng, ctx):
    return [
        ("Caller", "I have a clinical question about what's covered for a specific procedure code."),
        ("Agent", "That's best answered by our dental consultant team, I'll transfer you there now."),
    ]


def body_transfer_provider_relations(rng, ctx):
    return [
        ("Caller", "We want to discuss our contract terms as a provider, is that something you handle?"),
        ("Agent", "That falls under provider relations, let me get you over to that team."),
    ]


def body_transfer_complaints(rng, ctx):
    return [
        ("Caller", "I want to file a formal complaint about how a previous call was handled."),
        ("Agent", "I'm sorry to hear that. I'll connect you with our complaints team so they can log this properly."),
    ]


def body_preauth_general(rng, ctx):
    service = rng.choice(SERVICES)
    return [
        ("Caller", f"My dentist recommended {service} and wants a predetermination sent in first."),
        ("Agent", "Good call, that'll help avoid any surprise denials. Has the office already submitted the predetermination request?"),
        ("Caller", "Yes, a couple weeks ago."),
        ("Agent", "Let me check the status of that for you."),
    ]


def body_preauth_ortho(rng, ctx):
    amount = money(rng, 2000, 6500)
    return [
        ("Caller", "I'm calling about a pre-authorization for my daughter's orthodontic treatment."),
        ("Agent", f"I see the request here, the estimated treatment cost submitted was ${amount:.2f}."),
        ("Caller", "Right, and I wanted to know what portion would actually be covered."),
        ("Agent", "Let me calculate that based on your plan's orthodontic lifetime maximum."),
    ]


def body_cob_inquiry(rng, ctx):
    return [
        ("Caller", "My spouse and I both have benefits plans and I'm not sure how the coordination works."),
        ("Agent", "No problem, I can explain. Your plan pays first as the primary for you, and then whatever's left over can be claimed on your spouse's plan as secondary."),
        ("Caller", "Ah okay, that makes sense, I wasn't submitting to the second plan at all."),
        ("Agent", "That would definitely help recover some of the remaining balance."),
    ]


def body_direct_deposit(rng, ctx):
    return [
        ("Caller", "I want to set up direct deposit so I don't have to wait on cheques anymore."),
        ("Agent", "Absolutely, I can set that up. Can you confirm your banking institution and transit number?"),
        ("Caller", "Sure, one second, let me grab that info."),
        ("Agent", "Take your time, and once I have that I'll get it set up on your file."),
    ]


def body_address_update(rng, ctx):
    return [
        ("Caller", "I moved recently and need to update my mailing address on file."),
        ("Agent", "No problem, can I get your new address?"),
        ("Caller", "Yes, one second."),
        ("Agent", "Got it, that's updated on your file now."),
    ]


def body_eob_request(rng, ctx):
    return [
        ("Caller", "Can you send me an explanation of benefits for a claim from last month?"),
        ("Agent", "Sure, I can email that statement to you right away — can you confirm the email on file?"),
        ("Caller", "Yes, that's correct."),
        ("Agent", "Perfect, that's on its way to you now."),
    ]


def body_missing_cheque(rng, ctx):
    weeks_ago = rng.randint(3, 8)
    return [
        ("Caller", f"I never received a reimbursement cheque that was supposedly mailed out {weeks_ago} weeks ago."),
        ("Agent", "Let me check on that — I do see it was issued, but it hasn't been cashed."),
        ("Caller", "That's strange, it never showed up in my mailbox."),
        ("Agent", "I'll put in a stop-payment and reissue request, that usually takes 5-7 business days."),
    ]


def body_fax_confirmation(rng, ctx):
    return [
        ("Caller", "I sent over a fax with some claim documents yesterday, just wanted to confirm it was received."),
        ("Agent", "Let me check the fax queue... yes, I can confirm it came through and has been attached to the file."),
        ("Caller", "Great, thanks for confirming."),
    ]


def body_email_followup(rng, ctx):
    days_ago = rng.randint(4, 15)
    return [
        ("Caller", f"I emailed your team about {days_ago} days ago and haven't heard back."),
        ("Agent", "I'm sorry about the delay, let me look into what happened with that email."),
        ("Agent", rng.choice([
            "I see it in the queue, it just hasn't been actioned yet — I'll flag it for priority follow-up.",
            "I don't actually see a record of that coming through, let's resend it now while I'm on the line.",
        ])),
    ]


def body_provider_enrollment(rng, ctx):
    return [
        ("Caller", "We'd like to become a direct billing provider with your organization."),
        ("Agent", "Great, I can start that process. I'll need your clinic's business license and provider credentials."),
        ("Caller", "We can send those over today."),
        ("Agent", "Perfect, once received it typically takes 5-10 business days to complete enrollment."),
    ]


def body_claim_resubmission(rng, ctx):
    return [
        ("Caller", "A claim we submitted got rejected for a coding error, and we'd like to resubmit it."),
        ("Agent", "No problem, what was the rejection reason listed?"),
        ("Caller", "It said the procedure code didn't match the diagnosis code."),
        ("Agent", "Got it, let's correct that together and I'll help you resubmit it properly."),
    ]


def body_out_of_country(rng, ctx):
    country = rng.choice(["the United States", "Mexico", "the United Kingdom", "Portugal", "Italy"])
    amount = money(rng, 500, 8000)
    return [
        ("Caller", f"I had to get emergency treatment while traveling in {country} and want to submit a claim."),
        ("Agent", f"I'm sorry to hear that, let's get this started. Do you have itemized receipts for the ${amount:.2f} billed?"),
        ("Caller", "Yes, I have everything translated and itemized."),
        ("Agent", "Perfect, that'll speed up the review significantly since out-of-country claims need extra documentation."),
    ]


def body_plan_documents(rng, ctx):
    return [
        ("Caller", "Could you send me a copy of my plan booklet? I want to review what's covered."),
        ("Agent", "Of course, I'll email that over to you right away."),
        ("Caller", "Perfect, thank you."),
    ]


def body_general_complaint(rng, ctx):
    return [
        ("Caller", "I'm honestly pretty frustrated, this is the third time I've had to call about the same issue."),
        ("Agent", "I completely understand, and I'm sorry you've had to call multiple times. Let me pull up the full history on your file."),
        ("Caller", "I just want this actually resolved this time, not another promise."),
    ]


BODY_BUILDERS = {
    "claim_denial": body_claim_denial,
    "claim_general": body_claim_general,
    "benefit_balance": body_benefit_balance,
    "benefit_coverage": body_benefit_coverage,
    "benefit_eligibility": body_benefit_eligibility,
    "claim_status_submitted": body_claim_status_submitted,
    "claim_status_payment": body_claim_status_payment,
    "web_login": body_web_login,
    "web_submission": body_web_submission,
    "web_registration": body_web_registration,
    "web_navigation": body_web_navigation,
    "transfer_billing": body_transfer_billing,
    "transfer_dental": body_transfer_dental,
    "transfer_provider_relations": body_transfer_provider_relations,
    "transfer_complaints": body_transfer_complaints,
    "preauth_general": body_preauth_general,
    "preauth_ortho": body_preauth_ortho,
    "cob_inquiry": body_cob_inquiry,
    "direct_deposit": body_direct_deposit,
    "address_update": body_address_update,
    "password_reset": body_password_reset,
    "eob_request": body_eob_request,
    "missing_cheque": body_missing_cheque,
    "fax_confirmation": body_fax_confirmation,
    "email_followup": body_email_followup,
    "provider_enrollment": body_provider_enrollment,
    "claim_resubmission": body_claim_resubmission,
    "out_of_country": body_out_of_country,
    "plan_documents": body_plan_documents,
    "general_complaint": body_general_complaint,
}

INTRO_LINES = {
    "member": [
        "I have a question about a claim.", "I wanted to check on my benefits.",
        "I'm hoping you can help me with something.", "I have a quick question, if that's alright.",
    ],
    "provider": [
        "I have a question on behalf of our clinic.", "I'm calling about the provider portal.",
        "I need some help with a claim we submitted.", "I have something I'm hoping you can help with.",
    ],
}

ESCALATION_NOTE_TEMPLATES = [
    "Caller disputes {topic}; escalated to {coordinator} for review. Awaiting decision, callback may be required.",
    "Unable to resolve at first level — looped in {coordinator} re: {topic}. Notes added to file for follow-up.",
    "Escalated to {coordinator} due to {topic}; caller was firm on requesting a supervisor review.",
    "Put member on hold and consulted {coordinator} regarding {topic}. Outcome communicated to caller directly.",
]


def build_escalation_notes(rng, reason):
    coordinator = rng.choice(["Dental Coordinator", "Claims Team Lead", "Provider Relations Lead", "Complaints Coordinator"])
    return rng.choice(ESCALATION_NOTE_TEMPLATES).format(topic=reason["name"].lower(), coordinator=coordinator)


def daypart(hour):
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    return "evening"


def build_transcript(rng, reason, ctx):
    ctx["intro_line"] = rng.choice(INTRO_LINES["member" if ctx["caller_type"] == "plan_member" else "provider"])
    ctx["frustration_line"] = rng.choice([
        "Okay, I guess there's nothing else that can be done then.",
        "That's disappointing, but I appreciate you explaining it.",
        "Alright, I'll have to figure out next steps on my own then.",
    ])
    turns = opening_turns(rng, ctx)
    turns += build_body(reason["id"], rng, ctx)
    if ctx["escalated"]:
        turns += escalation_turns(rng, ctx)
    turns += closing_turns(rng, ctx)
    return [{"speaker": speaker, "text": text} for speaker, text in turns]


def generate_record(rng, index, start_date, end_date):
    reason = weighted_choice(rng, REASONS, [r["weight"] for r in REASONS])
    client = pick_client(rng, reason)
    caller_type = resolve_caller_type(rng, reason)

    escalation_prob = clamp(reason["escalation"] * ESCALATION_CLIENT_MULTIPLIER.get(client, 1.0), 0.02, 0.9)
    escalated = rng.random() < escalation_prob

    if escalated:
        resolution_status = weighted_choice(rng, ["resolved", "transferred", "unresolved"], [0.70, 0.20, 0.10])
    else:
        resolution_status = weighted_choice(rng, ["resolved", "transferred", "unresolved"], [0.80, 0.05, 0.15])

    low, high = reason["duration"]
    duration = rng.randint(low, high)
    if escalated:
        duration = int(duration * rng.uniform(1.3, 1.8))

    province = weighted_choice(rng, PROVINCES, PROVINCE_WEIGHTS)
    agent_id = weighted_choice(rng, AGENT_IDS, AGENT_WEIGHTS)
    timestamp = random_business_datetime(rng, start_date, end_date)

    caller_name = fake.first_name()
    provider_name = f"{fake.last_name()} {rng.choice(['Dental Clinic', 'Denture Clinic', 'Physiotherapy Clinic', 'Family Dental', 'Vision Centre'])}"

    ctx = {
        "client": client,
        "caller_type": caller_type,
        "agent_id": agent_id,
        "escalated": escalated,
        "resolution_status": resolution_status,
        "caller_name": caller_name,
        "provider_name": provider_name,
        "daypart": daypart(timestamp.hour),
    }

    transcript = build_transcript(rng, reason, ctx)
    escalation_notes = build_escalation_notes(rng, reason) if escalated else None

    return {
        "call_id": f"CC-{index:05d}",
        "timestamp": timestamp.isoformat(),
        "duration_seconds": duration,
        "caller_type": caller_type,
        "client": client,
        "call_reason": reason["name"],
        "escalated_to_coordinator": escalated,
        "escalation_notes": escalation_notes,
        "agent_id": agent_id,
        "caller_province": province,
        "resolution_status": resolution_status,
        "transcript": transcript,
        "sentiment_score": None,
        "complexity_score": None,
        "escalation_risk_flag": None,
    }


def print_summary(records):
    from collections import Counter

    total = len(records)
    escalated = sum(1 for r in records if r["escalated_to_coordinator"])
    resolved = sum(1 for r in records if r["resolution_status"] == "resolved")
    avg_duration = sum(r["duration_seconds"] for r in records) / total

    print(f"\nGenerated {total} records")
    print(f"Escalation rate: {escalated / total:.1%}")
    print(f"Resolution rate: {resolved / total:.1%}")
    print(f"Avg handle time: {avg_duration:.0f}s")

    print("\nCalls by client:")
    for client, count in Counter(r["client"] for r in records).most_common():
        print(f"  {client:<16} {count}")

    print("\nWeb-help calls by client:")
    web_help = [r for r in records if "Web portal" in r["call_reason"]]
    for client, count in Counter(r["client"] for r in web_help).most_common():
        print(f"  {client:<16} {count}")

    print("\nEscalations by client:")
    escalations = [r for r in records if r["escalated_to_coordinator"]]
    for client, count in Counter(r["client"] for r in escalations).most_common():
        print(f"  {client:<16} {count}")

    print("\nTop call reasons:")
    for reason, count in Counter(r["call_reason"] for r in records).most_common(8):
        print(f"  {reason:<45} {count}")


def main():
    rng = random.Random(SEED)
    end_date = datetime(2026, 8, 31)
    start_date = end_date - timedelta(days=182)

    records = [generate_record(rng, i + 1, start_date, end_date) for i in range(NUM_RECORDS)]
    records.sort(key=lambda r: r["timestamp"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")
    print_summary(records)


if __name__ == "__main__":
    main()
