import sys
# Force fresh import
if 'fake_news' in sys.modules:
    del sys.modules['fake_news']

from fake_news import FakeNewsAnalyzer

a = FakeNewsAnalyzer()

text = """Scientists Confirm That Nigerian Aunty Hand-clapping Is a Completely New Form of Quantum Communication. 
A joint research team from the University of Ibadan and CERN (via Zoom) published findings today claiming that 
the signature rapid hand-clapping pattern used by Nigerian aunties to summon children is actually a previously 
undetected form of quantum entanglement-based signaling. We observed over 4,700 clapping sequences across 14 states. 
When an aunty claps twice sharply followed by the slow triple-clap, children up to 800 meters away even through 
concrete walls experience an instantaneous compulsion to appear and say Yes ma. This defies classical physics. 
We are calling it Auntyon Entanglement. The paper suggests the phenomenon may be amplified by wrappers especially 
gele, palm oil residue on hands, and high levels of garri consumption. Follow-up experiments are planned to see 
if the same effect can be weaponized against husbands who forget anniversaries."""

r = a.analyze(text)
print(f"Fake News Probability: {r['probability']}%")
print(f"All factors: {r['factors'].keys()}")
print(f"Full result: {r}")
