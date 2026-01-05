# # main.py
# import json
# from decode import JmisbDecoder

# JARS = [
#     "jars/jmisb-api-1.12.0.jar",
#     "jars/jmisb-core-common-1.12.0.jar",
#     "jars/slf4j-api-1.7.36.jar",
#     "jars/slf4j-simple-1.7.36.jar",
# ]

# # INPUT_KLV = "output/standalone_metadata.klv"
# # OUTPUT_JSON = "output/standalone_decoded.json"

# INPUT_KLV = "output/metadata_emb.klv"
# OUTPUT_JSON = "output/embedded_decoded.json"


# def main():
#     decoder = JmisbDecoder(JARS)

#     decoder.start_jvm()
#     result = decoder.decode_file(INPUT_KLV)
#     decoder.shutdown_jvm()

#     with open(OUTPUT_JSON, "w") as f:
#         json.dump(result, f, indent=2)

#     print("✔ JSON output saved to", OUTPUT_JSON)


# if __name__ == "__main__":
#     main()

from pipeline import klv_metadata_pipeline

JARS = [
    "jars/jmisb-api-1.12.0.jar",
    "jars/jmisb-core-common-1.12.0.jar",
    "jars/slf4j-api-1.7.36.jar",
    "jars/slf4j-simple-1.7.36.jar",
]
if __name__ == "__main__":
    klv_metadata_pipeline(
        ts_path="embedded.ts",
        jars=JARS,
        output_dir="output",
    )

