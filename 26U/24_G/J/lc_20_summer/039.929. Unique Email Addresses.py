"""
039.929. Unique Email Addresses


Every email consists of a local name and a domain name, separated by the @ sign.

For example, in alice@leetcode.com, alice is the local name, and leetcode.com is the domain name.

Besides lowercase letters, these emails may contain '.'s or '+'s.

If you add periods ('.') between some characters in the local name part of 
an email address, mail sent there will be forwarded to the same address without dots in the local name.  
For example, "alice.z@leetcode.com" and "alicez@leetcode.com" 
forward to the same email address.  (Note that this rule does not apply for domain names.)

If you add a plus ('+') in the local name, everything after the first 
plus sign will be ignored. This allows certain emails to be filtered, 
for example m.y+name@email.com will be forwarded to my@email.com.  
(Again, this rule does not apply for domain names.)

It is possible to use both of these rules at the same time.

Given a list of emails, we send one email to each address in the list.  
How many different addresses actually receive mails? 

 

Example 1:

Input: ["test.email+alex@leetcode.com","test.e.mail+bob.cathy@leetcode.com","testemail+david@lee.tcode.com"]
Output: 2
Explanation: "testemail@leetcode.com" and "testemail@lee.tcode.com" actually receive mails
 

Note:

1 <= emails[i].length <= 100
1 <= emails.length <= 100
Each emails[i] contains exactly one '@' character.
All local and domain names are non-empty.
Local names do not start with a '+' character.

"""

def numUniqueEmails(self, emails: List[str]) -> int:
    l = []
    for email in emails:
        s = email.split("@")
        s1 = s[0].replace(".", "")
        email = s1.split("+")[0] + "@" + s[1]
        #email = s[0].replace(".", "").split("+")[0] + "@" + s[1]
        if email not in l:
            l.append(email)
    return len(l)

    seen = set()
    seen.add(local + '@' + domain)

    actual.add((local, domain))


def numUniqueEmails(self, emails):
    ans = set()
    for i in emails:
        tmp = ""
        local, domain = i.split('@')
        for j in local:
            if j == '.':
                continue
            if j == '+':
                break
            tmp += j
        ans.add(tmp + '@' + domain)
    return len(ans)


def numUniqueEmails(self, emails):
    hashset = set()
    num = 0
    for email in emails:
        email = email.split('@')
        part1 = email[0].replace('.', '')
        part2 = email[1]
        if '+' in part1:
            sep = '+'
            rest = part1.split(sep, 1)[0]
            finalres = rest+'@'+ part2
        else:
            finalres = part1+'@'+part2
        #print(finalres)
        if finalres not in hashset:
            hashset.add(finalres)
            
    return len(hashset)


























