## Critical Issues & Bug Fixes (1-10)

1. **How can I fix the hardcoded email recipient in EmailService that always sends to `nikoskoutsoukosprelorentzos@gmail.com` instead of the actual order creator?**

2. **The Resend API key is hardcoded in email_service.py - how should I move this to environment variables securely?**

3. **The `owner_uuid` field is not being set when tickets are created in the ticket repository - how can I fix this?**

4. **How can I implement proper transaction handling for order creation so that the ticket decrement operation is atomic with order creation?**

5. **The TicketStatus enum defines `ACTIVE`, `COMPLETED`, `EXPIRED` but the actual logic only uses `SCHEDULED`, `SCANNED`, `CANCELLED` - how should I clean this up?**

6. **How can I prevent race conditions when two users try to purchase the last ticket from an event simultaneously?**

7. **What's the best way to implement CORS restrictions instead of allowing all origins with `allow_origins=["*"]`?**

8. **How should I handle order expiration when an order is in progress and the APScheduler attempts to expire it while a user is trying to finalize it?**

9. **The database cascade delete behavior isn't defined - what happens when I delete a User who owns multiple Events and Orders?**

10. **How can I add proper logging to track when unexpected errors occur in critical operations like order finalization?**

---

## 🔧 Architecture & Design Improvements (11-20)

11. **How can I decouple the tight service dependencies so that OrderService doesn't directly depend on specific repository implementations?**

12. **Should I implement a dependency injection container or use FastAPI's dependency system more effectively?**

13. **How can I standardize error responses across all endpoints to provide consistent error codes and messages to clients?**

14. **What's the best pattern for handling business logic validation errors versus database errors?**

15. **The place overlap check logic seems like it could cause N+1 query problems - how can I optimize it for large datasets?**

16. **How should I implement state machine validation so that invalid order/event status transitions are prevented?**

17. **Should I create a BaseService class to consolidate common patterns like transaction handling and error management?**

18. **How can I implement request/response logging middleware to track all API calls for debugging?**

19. **What's the best way to handle pagination for `/all` endpoints that currently return unlimited results?**

20. **How should I structure database migrations for schema changes without breaking existing deployments?**

---

## 🔐 Security & Authentication (21-30)

21. **How can I implement JWT refresh tokens so users don't have to log in again when their 30-minute token expires?**

22. **The default `SECRET_KEY` in config.py should never be used in production - how should I enforce a strong secret requirement?**

23. **How can I implement rate limiting to prevent brute force attacks on the login endpoint?**

24. **Should I add API key authentication as an alternative to JWT for service-to-service communication?**

25. **How can I implement password strength validation rules (minimum length, complexity) in user registration?**

26. **The Google OAuth integration doesn't validate token expiration - how should I handle expired Google tokens?**

27. **How should I implement role-based access control (RBAC) more granularly (e.g., ORGANIZER_ADMIN vs ORGANIZER)?**

28. **What's the best way to implement audit logging to track who performed what action and when?**

29. **How can I prevent CSRF attacks on state-changing operations like order finalization?**

30. **Should I implement endpoint-level security with rate limiting per user or per IP address?**

---

## 📊 Database & Data Integrity (31-40)

31. **How should I implement soft deletes instead of hard deletes to preserve historical data?**

32. **The timezone handling assumes UTC - how can I support user-specific timezones for event dates?**

33. **How can I add database indexes to improve query performance for frequently searched fields?**

34. **Should I implement optimistic locking to detect concurrent modifications to events or orders?**

35. **How can I implement cascading updates/deletes properly (e.g., when a place is deleted, what happens to its events)?**

36. **The order cleanup scheduler runs every 1 minute - how can I monitor if it's falling behind or failing?**

37. **How should I validate that available ticket count never goes negative due to concurrent purchases?**

38. **What's the best strategy for handling duplicate order requests from network retries?**

39. **How can I implement data archival to move old completed orders to a separate archive table?**

40. **Should I add database query logging to identify slow or inefficient queries?**

---

## ✨ Feature Implementation (41-50)

41. **How should I implement a payment processing system that integrates with Stripe or PayPal while maintaining order state?**

42. **What's the best way to implement ticket transfers so customers can give their tickets to other users?**

43. **How can I implement event category filtering and search across multiple criteria (date, location, title)?**

44. **Should I add email notification templates and allow users to customize what notifications they receive?**

45. **How can I implement a waitlist system for sold-out events so users can be notified when tickets become available?**

46. **What's the best approach to implement bulk ticket creation and export functionality for organizers?**

47. **How should I implement event capacity dynamics (e.g., tiered pricing based on date ranges or availability)?**

48. **Can I add QR code validation with expiration times so tickets can't be scanned after the event ends?**

49. **How should I implement a refund policy system with partial refunds and refund reasons?**

50. **What's the best way to implement real-time notifications so users know when someone purchases their event's last tickets?**

---

## 📋 Testing & Documentation (Bonus Questions)

51. **How should I structure unit tests for the service layer while mocking repository dependencies?**

52. **What's the best approach to write integration tests that verify the entire order creation and finalization flow?**

53. **How can I implement API documentation that includes authentication examples and common error scenarios?**

54. **Should I create database fixtures for tests to ensure consistent test data?**

55. **How can I implement contract testing between frontend and backend API to ensure compatibility?**

---

## 🎯 Summary by Category

| Category | Questions | Focus |
|----------|-----------|-------|
| Critical Issues | 1-10 | Bugs, hardcoded values, data consistency |
| Architecture | 11-20 | Design patterns, performance, error handling |
| Security | 21-30 | Authentication, authorization, attack prevention |
| Database | 31-40 | Data integrity, migrations, optimization |
| Features | 41-50 | New functionality, integrations, user experience |
| Testing | 51-55 | Test strategy, documentation, quality |

---

## 💡 How to Use This List

1. **Pick a question** from the list that matches your current priority
2. **Ask me the question** exactly as written or in your own words
3. **I'll help you implement** the fix, feature, or improvement
4. **Iterate** through the list to progressively improve the application

Each question addresses a real pain point or improvement opportunity identified in the codebase analysis.
