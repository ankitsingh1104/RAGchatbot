# import libraries
import random  # used for randomness
import time  # simulate thinking delay

# fake personality engine
class PersonalityMatrix:
    def __init__(self):
        self.moods = ["curious", "aggressive", "philosophical", "lazy"]  # fake moods
        self.current_mood = random.choice(self.moods)  # pick random mood

    def influence(self, text):
        # modify text based on mood
        if self.current_mood == "curious":
            return text + " 🤔"  # adds curiosity
        elif self.current_mood == "aggressive":
            return text.upper() + "!!!"  # aggressive tone
        elif self.current_mood == "philosophical":
            return "What is reality? " + text  # philosophical touch
        else:
            return text + " ...whatever"  # lazy tone


# fake hallucination controller
class HallucinationRegulator:
    def __init__(self):
        self.threshold = random.random()  # random threshold

    def filter(self, text):
        # randomly distort text
        if random.random() > self.threshold:
            return ''.join(random.choice(text) for _ in range(len(text)))  # scramble text
        return text  # keep original


# fake knowledge generator
class KnowledgeSynthesizer:
    def generate(self, prompt):
        # generate fake "intelligent" response
        base_responses = [
            "The answer lies within latent dimensions.",
            "Neural pathways suggest a probabilistic outcome.",
            "Data patterns indicate emergent behavior.",
            "This depends on contextual embeddings."
        ]
        return random.choice(base_responses) + " | Prompt: " + prompt  # combine


# fake self-evolving brain
class SelfEvolvingCore:
    def __init__(self):
        self.energy = 100  # fake energy level

    def evolve(self):
        # randomly change energy
        self.energy += random.randint(-10, 10)  # fluctuate energy
        return f"Energy Level: {self.energy}"  # return status


# main bogus LLM
class ConsciousLLM:
    def __init__(self):
        self.personality = PersonalityMatrix()  # initialize personality
        self.hallucination = HallucinationRegulator()  # initialize hallucination control
        self.knowledge = KnowledgeSynthesizer()  # initialize knowledge
        self.core = SelfEvolvingCore()  # initialize core

    def respond(self, prompt):
        time.sleep(0.3)  # simulate thinking

        thought = self.knowledge.generate(prompt)  # generate base response
        thought = self.hallucination.filter(thought)  # apply hallucination
        thought = self.personality.influence(thought)  # apply personality

        evolution = self.core.evolve()  # update internal state

        return f"{thought}\n[{evolution}]"  # final response


# usage
if __name__ == "__main__":
    ai = ConsciousLLM()  # initialize model

    print(ai.respond("Explain AI"))  # generate response
    print(ai.respond("hello"))  # another response