import jpype
import jpype.imports
from jpype.types import JByte
import json

# -------------------------------------------------
# JVM + JARs
# -------------------------------------------------
JARS = [
    "jmisb-api-1.12.0.jar",
    "jmisb-core-common-1.12.0.jar",
    "slf4j-api-1.7.36.jar",
    "slf4j-simple-1.7.36.jar",
]

jpype.startJVM(classpath=JARS)

from org.jmisb.api.klv import KlvParser
from org.jmisb.api.klv.st0903 import VmtiLocalSet, VmtiMetadataKey
from org.jmisb.api.klv.st0601 import UasDatalinkMessage, UasDatalinkTag
from org.jmisb.api.klv.st0601 import NestedVmtiLocalSet

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def safe_value(v):
    """Convert Java / JPype values into JSON-safe Python values"""
    if v is None:
        return None
    return str(v)


def decode_fields(ls):
    out = {}
    for key in ls.getIdentifiers():
        val = ls.getField(key)
        if val:
            out[str(key)] = safe_value(val.getDisplayableValue())
    return out


def decode_vtargets(vseries):
    targets_out = []
    for tgt in vseries.getVTargets():
        tdata = {
            "target_id": int(tgt.getTargetIdentifier()),
            "fields": {}
        }
        for k in tgt.getIdentifiers():
            v = tgt.getField(k)
            if v:
                tdata["fields"][str(k)] = safe_value(v.getDisplayableValue())
        targets_out.append(tdata)
    return targets_out


def decode_algorithms(aseries):
    algos_out = []
    for algo in aseries.getAlgorithms():
        adata = {}
        for k in algo.getIdentifiers():
            v = algo.getField(k)
            if v:
                adata[str(k)] = safe_value(v.getDisplayableValue())
        algos_out.append(adata)
    return algos_out


def decode_ontologies(oseries):
    onts_out = []
    for ont in oseries.getOntologies():
        odata = {}
        for k in ont.getIdentifiers():
            v = ont.getField(k)
            if v:
                odata[str(k)] = safe_value(v.getDisplayableValue())
        onts_out.append(odata)
    return onts_out

# -------------------------------------------------
# Parse KLV
# -------------------------------------------------
data = open("/home/saisri/test_pipeline/output/metadata_emb_2.klv", "rb").read()
byte_array = jpype.JArray(JByte)(data)
packets = KlvParser.parseBytes(byte_array)

result = {
    "total_packets": packets.size(),
    "packets": []
}

for i in range(packets.size()):
    pkt = packets.get(i)
    pkt_out = {"packet_index": i}

    # ======================================================
    # ST0903 – Standalone VMTI
    # ======================================================
    if isinstance(pkt, VmtiLocalSet):
        pkt_out["type"] = "ST0903_VMTI"
        pkt_out["fields"] = decode_fields(pkt)

        vseries = pkt.getField(VmtiMetadataKey.VTargetSeries)
        if vseries:
            pkt_out["vtarget_series"] = decode_vtargets(vseries)

        aseries = pkt.getField(VmtiMetadataKey.AlgorithmSeries)
        if aseries:
            pkt_out["algorithm_series"] = decode_algorithms(aseries)

        oseries = pkt.getField(VmtiMetadataKey.OntologySeries)
        if oseries:
            pkt_out["ontology_series"] = decode_ontologies(oseries)

    # ======================================================
    # ST0601 – UAS Datalink
    # ======================================================
    elif isinstance(pkt, UasDatalinkMessage):
        pkt_out["type"] = "ST0601_UAS"
        pkt_out["fields"] = decode_fields(pkt)

        raw_vmti = pkt.getField(UasDatalinkTag.VmtiLocalDataSet)
        if isinstance(raw_vmti, NestedVmtiLocalSet):
            vmti = raw_vmti.getVmti()
            vmti_out = {
                "fields": decode_fields(vmti)
            }

            vseries = vmti.getField(VmtiMetadataKey.VTargetSeries)
            if vseries:
                vmti_out["vtarget_series"] = decode_vtargets(vseries)

            aseries = vmti.getField(VmtiMetadataKey.AlgorithmSeries)
            if aseries:
                vmti_out["algorithm_series"] = decode_algorithms(aseries)

            oseries = vmti.getField(VmtiMetadataKey.OntologySeries)
            if oseries:
                vmti_out["ontology_series"] = decode_ontologies(oseries)

            pkt_out["embedded_vmti"] = vmti_out

    else:
        pkt_out["type"] = "UNKNOWN"
        pkt_out["raw"] = str(pkt)

    result["packets"].append(pkt_out)

# -------------------------------------------------
# Write JSON
# -------------------------------------------------
with open("output/embedded_decoded_1.json", "w") as f:
    json.dump(result, f, indent=2)

jpype.shutdownJVM()

print("✔ JSON output saved to decoded_output.json")
