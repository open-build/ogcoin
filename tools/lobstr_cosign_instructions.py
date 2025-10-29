#!/usr/bin/env python3
"""
Lobstr Co-Signing Instructions
Since your account requires Lobstr's co-signature, here's how to get them to sign.
"""

print("""
🔐 LOBSTR CO-SIGNATURE REQUIRED
================================

Your account setup:
- Your key weight: 10
- Lobstr key weight: 100
- Required threshold: 20

The XDR is signed with your key (weight 10) but needs Lobstr's signature.

📱 HOW TO GET LOBSTR TO CO-SIGN:

Option 1: Lobstr Mobile App
--------------------------
1. Open Lobstr mobile app
2. Look for "Pending Transactions" or "Multi-Sig" section
3. You should see this transaction waiting for approval
4. Tap to review and approve the transaction

Option 2: Lobstr Web Interface  
-----------------------------
1. Go to lobstr.co and login
2. Look for notifications or pending transactions
3. Find the transaction requiring your approval
4. Review and approve it

Option 3: Contact Lobstr Support
-------------------------------
If you don't see pending transactions:
1. Copy this XDR and contact Lobstr support
2. Explain you need them to co-sign a transaction
3. Provide the XDR for them to add their signature

Option 4: Submit Through Lobstr's XDR Tool
-----------------------------------------
1. In Lobstr app/web, look for "Submit Transaction" or "XDR" tool
2. Paste this XDR:
   AAAAAgAAAABE4Lp3/K2LMIToMgcAidu6IZNv0S/8XXHgLe5W8KZgigABhqACQdKFAABf/QAAAAAAAAAAAAAAAQAAAAEAAAAAROC6d/ytizCE6DIHAInbuiGTb9Ev/F1x4C3uVvCmYIoAAAAAAAAAAAOc2CGAOOYn63PwEPOdbnJcAXCDuqcXxg8jEmMNIE8kAAAAAAHJw4AAAAAAAAAAAfCmYIoAAABAW+/LCaEE8WljK3pD/TkUO9L+DILyCUfyZcjZGuGSxIBHJQ0+KFF5uC9LbCn9gyk4EZsOJY+W+FWwqTKSav1qDw==
3. Submit it (Lobstr should automatically add their signature)

🚨 WHAT THIS TRANSACTION DOES:
- Creates account: GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N
- Funds it with: 3 XLM
- Cost: 0.01 XLM fee

Once this transaction is successful, we'll repeat for the other 2 accounts!
""")