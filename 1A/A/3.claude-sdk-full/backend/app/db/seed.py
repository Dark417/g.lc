"""Mock data. Small on purpose: enough for the agent to answer interesting questions."""

CUSTOMERS = [
    (1, "Ada Lovelace", "ada@example.com", "enterprise", "2024-01-15"),
    (2, "Grace Hopper", "grace@example.com", "pro", "2024-03-02"),
    (3, "Linus Torvalds", "linus@example.com", "free", "2024-05-20"),
    (4, "Margaret Hamilton", "margaret@example.com", "pro", "2024-06-11"),
    (5, "Ken Thompson", "ken@example.com", "free", "2024-09-01"),
]

ORDERS = [
    (101, 1, "Trail Backpack 40L", 149.00, "delivered", "2024-02-01"),
    (102, 1, "Down Sleeping Bag", 229.00, "delivered", "2024-02-01"),
    (103, 2, "Titanium Cook Set", 89.50, "shipped", "2024-08-14"),
    (104, 2, "Headlamp 400lm", 39.99, "delivered", "2024-08-14"),
    (105, 3, "Water Filter", 44.00, "returned", "2024-07-03"),
    (106, 4, "Trail Backpack 40L", 149.00, "delivered", "2024-07-19"),
    (107, 4, "Trekking Poles", 79.00, "pending", "2024-09-10"),
    (108, 1, "Merino Base Layer", 65.00, "shipped", "2024-09-12"),
    (109, 5, "Headlamp 400lm", 39.99, "delivered", "2024-09-15"),
    (110, 2, "Down Sleeping Bag", 229.00, "pending", "2024-09-18"),
]
