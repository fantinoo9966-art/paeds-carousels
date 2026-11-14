"""One-time helper (run on your own computer): pull the important paediatric drugs out of the
PedDose HTML file, in posting order, and save them ENCRYPTED to data/drugs.enc.

Usage: python tools/extract_drugs.py <PedDose.html> <DRUGS_KEY>
The plain text is never written to the repo; only the encrypted file is.
"""
import json
import re
import sys
from pathlib import Path

from cryptography.fernet import Fernet

# Posting order: most important / most used drugs in Indian paediatric practice first.
# Each entry is the start of the drug's name in the source file.
PRIORITY = [
    "ACETAMINOPHEN", "IBUPROFEN", "AMOXICILLIN", "ALBUTEROL", "ONDANSETRON", "CEFTRIAXONE",
    "AZITHROMYCIN", "PREDNISOLONE", "ZINC", "EPINEPHRINE", "AMPICILLIN", "GENTAMICIN",
    "MIDAZOLAM", "PHENOBARBITAL", "CAFFEINE CITRATE", "PHYTONADIONE", "CEFOTAXIME",
    "VANCOMYCIN", "MEROPENEM", "LEVETIRACETAM", "PHENYTOIN", "LORAZEPAM", "DIAZEPAM",
    "DEXAMETHASONE", "HYDROCORTISONE", "METHYLPREDNISOLONE", "BUDESONIDE", "IPRATROPIUM",
    "MONTELUKAST", "MAGNESIUM SULFATE", "AMINOPHYLLINE", "ADENOSINE", "ATROPINE",
    "AMIODARONE", "DOPAMINE", "DOBUTAMINE", "NOREPINEPHRINE", "MILRINONE", "DIGOXIN",
    "FUROSEMIDE", "SPIRONOLACTONE", "CAPTOPRIL", "ENALAPRIL", "AMLODIPINE", "NIFEDIPINE",
    "LABETALOL", "PROPRANOLOL", "ACYCLOVIR", "FLUCONAZOLE", "AMPHOTERICIN B, LIPOSOMAL",
    "OSELTAMIVIR", "METRONIDAZOLE", "SULFAMETHOXAZOLE", "CLOXACILLIN", "CEFIXIME",
    "CEFUROXIME", "CEFAZOLIN", "PIPERACILLIN", "AMIKACIN", "CIPROFLOXACIN", "CLINDAMYCIN",
    "LINEZOLID", "DOXYCYCLINE", "ISONIAZID", "RIFAMPIN", "PYRAZINAMIDE", "ETHAMBUTOL",
    "ALBENDAZOLE", "IVERMECTIN", "CHLOROQUINE", "PRIMAQUINE", "ARTESUNATE",
    "IMMUNE GLOBULIN", "ASPIRIN", "HEPARIN", "ENOXAPARIN", "MORPHINE", "FENTANYL",
    "KETAMINE", "NALOXONE", "FLUMAZENIL", "ACETYLCYSTEINE", "CHARCOAL", "DEFEROXAMINE",
    "PRALIDOXIME", "CALCIUM GLUCONATE", "SODIUM BICARBONATE", "POTASSIUM SUPPLEMENTS",
    "INSULIN", "DEXTROSE", "GLUCAGON", "MANNITOL", "IRON―ORAL",
    "FOLIC ACID", "CHOLECALCIFEROL", "VITAMIN A", "CALCITRIOL", "LEVOTHYROXINE",
    "DESMOPRESSIN", "OCTREOTIDE", "VASOPRESSIN", "ALPROSTADIL", "INDOMETHACIN",
    "OMEPRAZOLE", "PANTOPRAZOLE", "RANITIDINE", "LACTULOSE", "POLYETHYLENE GLYCOL",
    "CETIRIZINE", "CHLORPHENIRAMINE", "DIPHENHYDRAMINE", "HYDROXYZINE", "PROMETHAZINE",
    "VALPROIC ACID", "CARBAMAZEPINE", "TOPIRAMATE", "CLOBAZAM", "BACLOFEN",
    "METHYLPHENIDATE", "MELATONIN", "HYDROXYUREA", "TRANEXAMIC ACID", "ALTEPLASE",
    "SUCCINYLCHOLINE", "ROCURONIUM", "VECURONIUM", "PROPOFOL", "THIOPENTAL", "LIDOCAINE",
    "SILDENAFIL", "BOSENTAN", "ALBUMIN", "ACETAZOLAMIDE", "ALLOPURINOL", "COLISTIMETHATE",
    "TOBRAMYCIN", "ERYTHROMYCIN", "PENICILLIN G", "NITROFURANTOIN", "MUPIROCIN",
    "PERMETHRIN", "NYSTATIN", "CLOTRIMAZOLE", "GANCICLOVIR", "ZIDOVUDINE", "NEVIRAPINE",
]


def load(html_path: str) -> list[dict]:
    text = Path(html_path).read_text(encoding="utf-8")
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(m.group(1))["drugs"]


def main() -> None:
    html_path, key = sys.argv[1], sys.argv[2]
    drugs = load(html_path)
    chosen, seen = [], set()
    for want in PRIORITY:
        for d in drugs:
            if d["name"].upper().startswith(want) and d["name"] not in seen:
                seen.add(d["name"])
                chosen.append({
                    "name": d["name"], "class": d.get("cls", ""), "supplied": d.get("supplied", ""),
                    "dosing": d.get("dosing", ""), "remarks": d.get("renal", []),
                    "source_page": d.get("bookPage"),
                })
                break
        else:
            print(f"not found: {want}")
    blob = Fernet(key.encode()).encrypt(json.dumps(chosen, ensure_ascii=False).encode("utf-8"))
    out = Path(__file__).resolve().parent.parent / "data" / "drugs.enc"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(blob)
    print(f"Saved {len(chosen)} drugs (encrypted) to {out}")


if __name__ == "__main__":
    main()
