# These are the truth
truth_list = """
line 1
line 2
line 3
""".strip().split("\n")

except_list = """
line 1
line 2
""".strip().split("\n")


## Output is line 3

# # Normalization
# def normalize(name):
#     name = name.lower().strip()
#     # Replace en dash or em dash with a normal hyphen
#     name = name.replace(" – ", "-").replace("–", "-").replace("—", "-")
#     # Replace multiple spaces with single hyphen
#     name = name.replace(" ", "-")
#     return name

# truth_list = [normalize(x) for x in truth_list]
# except_list = [normalize(x) for x in except_list]

# Filter
filtered = sorted(set(truth_list) - set(except_list))

# Output
for i, name in enumerate(filtered, start=1):
    print(f'{{ "area": "{name}" }}')
    if i % 10 == 0:
        print("\n------\n")

print(f"\nTotal: {len(filtered)}\n")
