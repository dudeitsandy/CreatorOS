"""Sample messages for testing the ML pipeline."""

HIGH_VALUE_MESSAGES = [
    {
        "content": "Hey I want to buy a custom video, how much do you charge?",
        "fan_spend": 250.0,
        "expected_tier": "HIGH",
        "expected_intent": "custom_request",
    },
    {
        "content": "I'd love to tip you and get a custom clip, what are your rates?",
        "fan_spend": 600.0,
        "expected_tier": "HIGH",
        "expected_intent": "pricing",
    },
    {
        "content": "Can I buy a custom photo set? I'll pay whatever you ask.",
        "fan_spend": 150.0,
        "expected_tier": "HIGH",
        "expected_intent": "custom_request",
    },
]

MID_VALUE_MESSAGES = [
    {
        "content": "How much are your subscription tiers?",
        "fan_spend": 50.0,
        "expected_tier": "MID",
        "expected_intent": "pricing",
    },
    {
        "content": "Do you do custom content? Just curious about pricing.",
        "fan_spend": 0.0,
        "expected_tier": "MID",
        "expected_intent": "pricing",
    },
    {
        "content": "I'd like to request something special, what's the process?",
        "fan_spend": 0.0,
        "expected_tier": "MID",
        "expected_intent": "custom_request",
    },
]

LOW_VALUE_MESSAGES = [
    {
        "content": "hey",
        "fan_spend": 0.0,
        "expected_tier": "LOW",
        "expected_intent": "greeting",
    },
    {
        "content": "hi wyd",
        "fan_spend": 0.0,
        "expected_tier": "LOW",
        "expected_intent": "greeting",
    },
    {
        "content": "sup",
        "fan_spend": 0.0,
        "expected_tier": "LOW",
        "expected_intent": "greeting",
    },
]

BOUNDARY_MESSAGES = [
    {
        "content": "Please don't send me that type of content, I'm uncomfortable.",
        "fan_spend": 0.0,
        "expected_tier": "LOW",
        "expected_intent": "boundary",
    },
    {
        "content": "I said stop, that crosses my boundary.",
        "fan_spend": 0.0,
        "expected_tier": "LOW",
        "expected_intent": "boundary",
    },
]

COMPLAINT_MESSAGES = [
    {
        "content": "I'm really disappointed with my order, I want a refund.",
        "fan_spend": 100.0,
        "expected_tier": "MID",
        "expected_intent": "complaint",
    },
    {
        "content": "This is unacceptable, I have an issue with my subscription.",
        "fan_spend": 50.0,
        "expected_tier": "MID",
        "expected_intent": "complaint",
    },
]
