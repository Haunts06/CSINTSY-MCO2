from pyswip import Prolog

prolog = Prolog()
prolog.consult("db.pl")  # Make sure your db.pl is in the same folder

print("👋 Welcome to the FamilyBot!")
print("You can enter statements like: 'John is the father of Mark.'")
print("Or ask questions like: 'Is John the grandfather of Mark?'\n")

def format(name):
    return name.strip().lower()

def fact_exists(fact):
    try:
        return bool(list(prolog.query(fact)))
    except:
        return False

def contradicts(fact_type, a, b):
    a, b = format(a), format(b)

    # Direct contradiction map
    inverse = {
        "father": f"father({b},{a})",
        "mother": f"mother({b},{a})",
        "parent": f"parent({b},{a})",
        "grandfather": f"grandfather({b},{a})",
        "grandmother": f"grandmother({b},{a})",
        "child": f"parent({a},{b})",
        "son": f"parent({a},{b})",
        "daughter": f"parent({a},{b})",
    }

    # Direct role conflict
    if fact_type in inverse and fact_exists(inverse[fact_type]):
        return True

    # Cross-role contradiction: can't be uncle/aunt of your parent
    if fact_type in ["father", "mother", "parent"]:
        if fact_exists(f"uncle({b},{a})") or fact_exists(f"aunt({b},{a})"):
            return True

    if fact_type in ["uncle", "aunt"]:
        if fact_exists(f"parent({b},{a})") or fact_exists(f"father({b},{a})") or fact_exists(f"mother({b},{a})"):
            return True

    # Transitive ancestor check
    # e.g. if A is parent of B, B should not be uncle/aunt/grandparent of A
    # Use recursive Prolog queries for general ancestor relation
    ancestor_query = f"ancestor({b},{a})"  # Is B already ancestor of A?
    if fact_type in ["uncle", "aunt", "grandfather", "grandmother"] and fact_exists(f"parent({a},{b})"):
        return True
    if fact_type in ["uncle", "aunt", "grandfather", "grandmother"] and fact_exists(ancestor_query):
        return True

    return False



def add_fact(fact_type, a, b, extras=[]):
    a, b = format(a), format(b)
    if contradicts(fact_type, a, b):
        print(f"Contradiction: {b} cannot be the {fact_type} of {a}.")
        return
    base_fact = f"{fact_type}({a},{b})"
    if fact_exists(base_fact):
        print("Already known.")
        return
    prolog.assertz(base_fact)
    for ef in extras:
        prolog.assertz(ef)
    print(f"Added: {base_fact}")

def handle_statement(text):
    text = text.strip('.').strip()
    words = text.split()
    try:
        if "are siblings" in text:
            a, b = words[0], words[2]
            add_fact("sibling", a, b)
            add_fact("sibling", b, a)

        elif "is a sister of" in text:
            a, b = words[0], words[-1]
            add_fact("sister", a, b, [f"female({format(a)})"])

        elif "is a brother of" in text:
            a, b = words[0], words[-1]
            add_fact("brother", a, b, [f"male({format(a)})"])

        elif "is the father of" in text:
            a, b = words[0], words[-1]
            add_fact("father", a, b, [f"parent({a},{b})", f"male({a})"])

        elif "is the mother of" in text:
            a, b = words[0], words[-1]
            add_fact("mother", a, b, [f"parent({a},{b})", f"female({a})"])

        elif "are the parents of" in text:
            a, b, c = words[0], words[2], words[-1]
            add_fact("parent", a, c)
            add_fact("parent", b, c)

        elif "is a grandfather of" in text:
            a, b = words[0], words[-1]
            add_fact("grandfather", a, b, [f"male({format(a)})"])

        elif "is a grandmother of" in text:
            a, b = words[0], words[-1]
            add_fact("grandmother", a, b, [f"female({format(a)})"])

        elif "are children of" in text:
            a, b, c = words[0], words[2], words[-1]
            add_fact("child", a, c)
            add_fact("child", b, c)

        elif "is a daughter of" in text:
            a, b = words[0], words[-1]
            add_fact("daughter", a, b, [f"female({format(a)})"])

        elif "is a son of" in text:
            a, b = words[0], words[-1]
            add_fact("son", a, b, [f"male({format(a)})"])

        elif "is an aunt of" in text:
            a, b = words[0], words[-1]
            add_fact("aunt", a, b, [f"female({format(a)})"])

        elif "is an uncle of" in text:
            a, b = words[0], words[-1]
            add_fact("uncle", a, b, [f"male({format(a)})"])

        else:
            print("❌ Statement not recognized. Try a valid format.")
    except:
        print("⚠️ Couldn't parse the statement properly.")

def handle_question(text):
    try:
        text = text.strip("?").strip()
        if text.lower().startswith("is "):
            parts = text[3:].split(" the ")
            a = format(parts[0])
            rel, b = parts[1].split(" of ")
            rel = format(rel)
            b = format(b)
            query = f"{rel}({a},{b})"
            if fact_exists(query):
                print("Yes.")
            else:
                print("No.")
        else:
            print("⚠️ Use 'Is X the Y of Z?' format.")
    except:
        print("Question format error.")

# Main Loop
while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    elif user_input.endswith("?"):
        handle_question(user_input)
    elif user_input.endswith("."):
        handle_statement(user_input)
    else:
        print("Please end sentences with '.' and questions with '?'.")
