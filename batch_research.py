import urllib.request
import json
import time

questions = [
    "Can arguments made by counsel be treated as established facts by the High Court?",
    "What did the Supreme Court hold in Commissioner of Income-Tax, West Bengal v. Calcutta Agency Ltd.?",
    "Why did the Supreme Court find the High Court's approach improper in Calcutta Agency?",
    "What facts were relied upon by the Tribunal, and how did the High Court treat counsel's arguments?",
    "What was the Supreme Court's reasoning for reversing the High Court's judgment?",
    "Identify the passage where the Supreme Court discusses treating counsel's arguments as facts.",
    "Does the judgment support the proposition that a court may rely on an advocate's submissions as evidence?",
    "What is the distinction in the judgment between facts and arguments made by counsel?",
    "Summarize the Court's holding and provide the strongest supporting passage.",
    "Give me the exact passage supporting the Court's conclusion, with the case citation and page range."
]

url = 'http://127.0.0.1:8000/api/research'
headers = {'Content-Type': 'application/json'}

with open('d:\\legal-research-engine\\research_results.txt', 'w', encoding='utf-8') as f:
    f.write("LEXIS AI - LEGAL RESEARCH REPORT\n")
    f.write("=================================\n\n")

    for i, q in enumerate(questions, 1):
        print(f"Processing question {i}/10...")
        data = json.dumps({'query': q}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            res = urllib.request.urlopen(req)
            res_data = json.loads(res.read().decode('utf-8'))
            
            f.write(f"Q{i}: {q}\n")
            f.write("-" * 80 + "\n")
            f.write(f"ANSWER:\n{res_data.get('answer')}\n\n")
            
            q_gate = res_data.get('quote_gate', 'N/A')
            verifier = res_data.get('verification', 'N/A')
            f.write(f"[ Verification ] Quote Gate: {q_gate} | Legal Verifier: {verifier}\n\n")
            
            evidence = res_data.get('evidence', [])
            if evidence:
                f.write("EVIDENCE:\n")
                for idx, ev in enumerate(evidence, 1):
                    f.write(f"  {idx}. Case: {ev.get('title')} ({ev.get('citation')})\n")
                    f.write(f"     Pages: {ev.get('page_start')}-{ev.get('page_end')}\n")
            
            f.write("=" * 80 + "\n\n")
            
        except Exception as e:
            print(f"Error on question {i}: {e}")
            f.write(f"Q{i}: {q}\n")
            f.write(f"ERROR: Failed to retrieve answer. ({e})\n\n")
            f.write("=" * 80 + "\n\n")

print("Finished generating report.")
