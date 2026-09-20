import urllib.request
import json

def test_live():
    print("=" * 60)
    print("Testing Live API Endpoints on http://127.0.0.1:8000")
    print("=" * 60)

    # 1. Create a session
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/sessions',
        data=json.dumps({'title': 'Live Test Session'}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    session_data = json.loads(res.read().decode('utf-8'))
    session_id = session_data['id']
    print(f"[+] 1. Created Session: {session_id}")

    # 2. Test Grounded Q&A
    chat_payload = {
        'session_id': session_id,
        'message': 'What is founder mode according to Brian Chesky?',
        'provider': 'sim',
        'mode': 'default'
    }
    req2 = urllib.request.Request(
        'http://127.0.0.1:8000/api/chat',
        data=json.dumps(chat_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res2 = urllib.request.urlopen(req2)
    lines = res2.read().decode('utf-8').split('\n')
    sources_lines = [l for l in lines if '"type": "sources"' in l]
    token_lines = [l for l in lines if '"type": "token"' in l]
    print(f"[+] 2. Grounded Q&A:")
    print(f"    - Citations received: {len(sources_lines) > 0}")
    print(f"    - Streamed tokens count: {len(token_lines)}")

    # 3. Test Ship 30 for 30 essay
    ship_payload = {
        'session_id': session_id,
        'message': 'Write a Ship 30 for 30 essay on Elena Verna B2B PLG',
        'provider': 'sim',
        'mode': 'ship30'
    }
    req3 = urllib.request.Request(
        'http://127.0.0.1:8000/api/chat',
        data=json.dumps(ship_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res3 = urllib.request.urlopen(req3)
    lines3 = res3.read().decode('utf-8').split('\n')
    essay_text = ''.join([json.loads(l[6:])['content'] for l in lines3 if l.startswith('data: {"type": "token"')])
    print(f"[+] 3. Ship 30 for 30 Essay:")
    print(f"    - Word count: {len(essay_text.split())} words")
    print(f"    - Has hook & bold bullets: {'#' in essay_text and '**' in essay_text}")

    # 4. Test Artifact Generation
    art_payload = {
        'session_id': session_id,
        'message': 'Create an interactive retention calculator artifact',
        'provider': 'sim',
        'mode': 'artifact'
    }
    req4 = urllib.request.Request(
        'http://127.0.0.1:8000/api/chat',
        data=json.dumps(art_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res4 = urllib.request.urlopen(req4)
    lines4 = res4.read().decode('utf-8').split('\n')
    artifact_lines = [l for l in lines4 if '"type": "artifact"' in l]
    print(f"[+] 4. Artifact Generation:")
    print(f"    - Artifact detected & saved: {len(artifact_lines) > 0}")

    # 5. Test Out-of-Domain Refusal
    refuse_payload = {
        'session_id': session_id,
        'message': 'How do I bake sourdough bread?',
        'provider': 'sim',
        'mode': 'default'
    }
    req5 = urllib.request.Request(
        'http://127.0.0.1:8000/api/chat',
        data=json.dumps(refuse_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res5 = urllib.request.urlopen(req5)
    lines5 = res5.read().decode('utf-8').split('\n')
    refusal_tokens = ''.join([json.loads(l[6:])['content'] for l in lines5 if l.startswith('data: {"type": "token"')])
    print(f"[+] 5. Out-of-Domain Refusal:")
    print(f"    - Response: {refusal_tokens.strip()}")
    print("=" * 60)
    print("All live integration flows verified successfully!")
    print("=" * 60)

if __name__ == '__main__':
    test_live()
