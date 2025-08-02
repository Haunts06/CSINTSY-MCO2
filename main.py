from pyswip import Prolog

prolog = Prolog()
prolog.consult("db.pl")  # Make sure your db.pl is in the same folder

print("Welcome to the FamilyBot!")
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

    # Forbidden reverse relationships
    contradictions = {
        "father": [f"mother({a},{b})", f"female({a})"],
        "mother": [f"father({a},{b})", f"male({a})"],
        "son": [f"daughter({a},{b})", f"female({a})"],
        "daughter": [f"son({a},{b})", f"male({a})"],
        "uncle": [f"aunt({a},{b})", f"female({a})"],
        "aunt": [f"uncle({a},{b})", f"male({a})"],
    }

    for contradiction in contradictions.get(fact_type, []):
        if fact_exists(contradiction):
            return True

    if fact_type in ["uncle", "aunt", "grandfather", "grandmother"]:
        if fact_exists(f"ancestor({b},{a})"):
            return True

    return False


def add_fact(fact_type, a, b=None):
    a = format(a)
    if b is not None:
        b = format(b)
    
    # Skip contradiction check for gender
    if b and contradicts(fact_type, a, b):
        print(f"Contradiction: {b} cannot be the {fact_type} of {a}.")
        return
    
    base_fact = f"{fact_type}({a})" if b is None else f"{fact_type}({a},{b})"
    
    if fact_exists(base_fact):
        print("Already known.")
        return
    
    prolog.assertz(base_fact)
    print(f"Learned: {base_fact}")


def handle_statement(text):
    text = text.strip('.').strip()
    words = text.split()
    try:
        if "are siblings" in text:
            a, b = words[0], words[2]
            add_fact("sibling_fact", a, b)
            add_fact("sibling_fact", b, a)

        elif "is a sister of" in text:
            a, b = words[0], words[-1]
            add_fact("sibling_fact", a, b)
            add_fact("female", a)

        elif "is a brother of" in text:
            a, b = words[0], words[-1]
            add_fact("sibling_fact", a, b)
            add_fact("male", a)

        elif " is the father of " in text:
            a, b = words[0], words[-1]
            add_fact("parent", a, b)
            add_fact("male", a)

        elif " is the mother of " in text:
            a, b = words[0], words[-1]
            add_fact("parent", a, b)
            add_fact("female", a)

        elif "are the parents of" in text:
            a, b, c = words[0], words[2], words[-1]
            add_fact("parent", a, c)
            add_fact("parent", b, c)

        elif "is a grandfather of" in text:
            a, b = words[0], words[-1]
            add_fact("grandparent", a, b)
            add_fact("grandfather", a, b)
            add_fact("male", a)

        elif "is a grandmother of" in text:
            a, b = words[0], words[-1]
            add_fact("grandparent", a, b)
            add_fact("grandmother", a, b)
            add_fact("female", a)

        elif "are children of" in text:
            a, b, c = words[0], words[2], words[-1]
            add_fact("child", a, c)
            add_fact("child", b, c)

        elif "is a daughter of" in text:
            a, b = words[0], words[-1]
            add_fact("daughter", a, b)
            add_fact("child", a, b)
            add_fact("parent", b, a)
            add_fact("female", a)

        elif "is a son of" in text:
            a, b = words[0], words[-1]
            add_fact("son", a, b)
            add_fact("child", a, b)
            add_fact("parent", b, a)
            add_fact("male", a)

        elif "is an aunt of" in text:
            a, b = words[0], words[-1]
            add_fact("aunt", a, b)
            add_fact("female", a)

        elif "is an uncle of" in text:
            a, b = words[0], words[-1]
            add_fact("uncle", a, b)
            add_fact("male", a)

        else:
            print("Statement invalid.")

    except Exception as e:
        print(f"Error processing statement: {e}")
        # print("Could not parse statement. Please use the correct format.")

def conflicting_gender(name):
    return fact_exists(f"male({name})") and fact_exists(f"female({name})")

def handle_question(text):
    try:
        text = text.strip("?").strip()

        # Pattern 1: Is ___ a/an ___ of ___? / Is ___ the ___ of ___?
        if text.lower().startswith("is ") and (" a " in text or " an " in text or " the " in text):
            capture = text[3:]
            determiner = None
            if " the " in capture:
                determiner = " the "
            elif " a " in capture:
                determiner = " a "
            elif " an " in capture:
                determiner = " an "

            if determiner is None:
                print("Question format not recognized.")
                return

            parts = capture.split(determiner)
            if len(parts) == 2 and " of " in parts[1]:
                a = format(parts[0])
                rel, b = parts[1].split(" of ")
                rel = format(rel)
                b = format(b)
                query = f"{rel}({a},{b})"
                print("Yes.") if fact_exists(query) else print("No.")


        # Pattern 2: Who are the siblings/sisters/brothers/daughters/sons/children of ___?
        elif text.lower().startswith("who are the"):
            lowered = text.lower().rstrip("?")
            roles = ["siblings", "sisters", "brothers", "daughters", "sons", "children", "parents"]

            role_matched = next((role for role in roles if role in lowered), None)
            if not role_matched:
                print("Please ask about siblings, sisters, brothers, daughters, sons, or children.")
                return

            try:
                name_part = lowered.split(f"the {role_matched} of")[1].strip()
                name = format(name_part)

                # Map the query roles to Prolog predicates
                role_to_predicate = {
                    "siblings": "related_sibling",
                    "sisters": "sister",
                    "brothers": "brother",
                    "daughters": "daughter",
                    "sons": "son",
                    "children": "child",
                    "parents": "parent"
                }

                pred = role_to_predicate[role_matched]
                results = list(prolog.query(f"{pred}(X, {name})"))

                others = sorted(set(res['X'] for res in results if res['X'] != name))

                if others:
                    print(f"{name.capitalize()}'s {role_matched} are: {', '.join(others)}.")
                else:
                    print(f"{name.capitalize()} has no known {role_matched}.")
            except Exception:
                print(f"Please follow the format: 'Who are the {role_matched} of <Name>?'.")


        # Pattern 3: Are ___ and ___ siblings/relatives?
        elif text.lower().startswith("are ") and ("sibling" in text.lower() or "relative" in text.lower()):
            lowered = text.lower().rstrip("?")
            
            relation = "sibling" if "sibling" in lowered else "relative"
            capture = lowered.split(relation)[0][4:].strip()
            
            if " and " in capture:
                names = capture.split(" and ")
            elif " & " in capture:
                names = capture.split(" & ")
            else:
                print("Please use 'and' or '&' to separate two names.")
                return

            if len(names) != 2:
                print("Please provide exactly two names.")
                return

            a, b = format(names[0].strip()), format(names[1].strip())

            relation_query = {
                "sibling": [f"related_sibling({a}, {b})", f"related_sibling({b}, {a})"],
                "relative": [f"relative({a}, {b})", f"relative({b}, {a})"]
            }

            if any(fact_exists(q) for q in relation_query[relation]):
                print(f"Yes, {names[0]} and {names[1]} are {relation}s.")
            else:
                print(f"No, {names[0]} and {names[1]} are not {relation}s.")


        # Pattern 4: Are ___ and ___ the parents of ___?
        elif text.lower().startswith("are") and ("parents of" in text.lower() or "the parents of" in text.lower()):
            try:
                lowered = text.lower().rstrip("?").replace("the parents of", "parents of")
                capture = lowered[4:].strip()

                parents_part, child_part = capture.split("parents of")
                parent1, parent2 = [p.strip().lower() for p in parents_part.split("and")]
                child = child_part.strip().lower()

                a = format(parent1)
                b = format(parent2)
                c = format(child)

                # Direct query
                q1 = list(prolog.query(f"parent({c}, {a})"))
                q2 = list(prolog.query(f"parent({c}, {b})"))

                # Fallback: try if child relation implies parent
                if not q1:
                    q1 = list(prolog.query(f"child({a}, {c})"))
                    print("Fallback used for first parent")

                if not q2:
                    q2 = list(prolog.query(f"child({b}, {c})"))
                    print("Fallback used for second parent")

                if q1 and q2:
                    print(f"Yes, {parent1} and {parent2} are parents of {child}.")
                else:
                    print(f"No, {parent1} and {parent2} are not parents of {child}.")

            except Exception as e:
                print("Error parsing input:", e)


        # Pattern 5: Who is the mother/father of ___?
        elif text.lower().startswith("who is the ") and " of " in text.lower():
            lowered = text.lower().rstrip("?")
            roles = ["mother", "father"]

            role_matched = next((role for role in roles if role in lowered), None)
            if not role_matched:
                print("Please ask about the mother or father.")
                return

            try:
                name_part = lowered.split(f"the {role_matched} of")[1].strip()
                name = format(name_part)

                # Build the Prolog query like: mother(X, john)
                query = f"{role_matched}(X, {name})"
                results = list(prolog.query(query))

                parents = sorted(set(res['X'] for res in results if res['X'] != name))

                if parents:
                    print(f"{name.capitalize()}'s {role_matched} is: {parents[0]}.")
                else:
                    print(f"{name.capitalize()} has no known {role_matched}.")
            except Exception:
                print(f"Please follow the format: 'Who is the {role_matched} of <Name>?'.")

        # Pattern 6: Are ___, ___ and ___ children of ___?
        elif text.lower().startswith("are ") and " children of " in text.lower():
            try:
                lowered = text.lower().replace("?", "")
                parts = lowered.split(" children of ")
                people_part = parts[0].replace("are", "").strip()
                parent = format(parts[1].strip())
                
                tokens = people_part.replace(" and ", ",").split(",")
                children = [format(token.strip()) for token in tokens if token.strip()]

                all_match = True
                for child in children:
                    results = list(prolog.query(f"child({child}, {parent})"))
                    if not results:
                        all_match = False
                        break

                if all_match:
                    print(f"Yes, {', '.join(children)} are all children of {parent.capitalize()}.")
                else:
                    print(f"No, not all of them are children of {parent.capitalize()}.")
            except Exception:
                print("Please follow the format: Are <name1>, <name2> and <name3> children of <Parent>?")
        
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
