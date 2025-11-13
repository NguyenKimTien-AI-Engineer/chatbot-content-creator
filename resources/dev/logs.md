### MekongAI

```shell
### Notes Before Testing This Feature:
- Please ensure you are using a Facebook account with the **Tester role** in our app.
- If needed, you may use the following test Facebook account, which has been added as a Tester:
    + **Email**: khnh113a@gmail.com
    + **Password**: Tuandenk56
- If you have problems with your 2FA code, use the **Backup codes** below:
    + **Backup Code 1**: 2035 1061
    + **Backup Code 2**: 2366 5334
    + **Backup Code 3**: 3293 9232
    + **Backup Code 4**: 5191 0312
    + **Backup Code 5**: 5812 5637

- **Important**: It appears that in the previous review, the tester may not have used a Facebook account with the **Tester role** in our App (App ID: `1054545482977612`).
- Since our app is not yet public, it can only obtain an Access Token from users with the **Tester role** or equivalent for our related features when logging into Facebook.
- Therefore, if the tester does not use the designated account with the **Tester role**, the app will encounter an error as it still lacks the necessary permissions for public use with other users.
- Please use the provided Backup code to bypass 2FA authentication.

### Steps to Test This Feature on Our App:
1. Step 1: Visit the URL: https://mekongai-social-media-bot.vercel.app
2. Step 2: Click "Sign In" on the MenuBar. Register an account. Or log in with the Test account details below:
- Username: mekongai.dev.tester
- Password: Mekongai@testing001
=> Click "Sign In."
3. Step 3:
- Click the "Connect Facebook Account" button on the homepage.
- Log in with your Facebook account. Please ensure you are using a Facebook account with the **Tester role** in our app. If needed, you may use the following test Facebook account, which has already been added as a Tester:
- **Email**: khnh113a@gmail.com
- **Password**: Tuandenk56
- If you have problems with your 2FA code, use the **Backup codes** below:
- **Backup Code 1**: 2035 1061
- **Backup Code 2**: 2366 5334
- **Backup Code 3**: 3293 9232
- **Backup Code 4**: 5191 0312
- **Backup Code 5**: 5812 5637

- In the "Select the Page you want MekongAI to access" section, choose "Apply to all current and future Pages" or "Grant access only to specific current news Pages" and click "Continue."
- Click "Save" to confirm Page management permissions => "Understood."
4. Step 4: Click the "Dashboard" button on the MenuBar.
5. Step 5:
- Click on "Message Manager" in the left menu.
- In the Filter section, there is a "Select group/clan" Dropdown. Once clicked, it will display all Facebook accounts linked to the account along with the Pages granted access in Step 4.
- You can select the desired Page for our chatbot to automatically respond to messages sent to their Page => Click the "Auto reply Message" button to apply.

### Steps to Test the Message Reply Feature on Our App Page:
1. **Step 1**: Log in with the Facebook account linked in Step 3 (use the provided test account if needed).
2. **Step 2**:
- Visit the Page registered with "Auto reply Message" in Step 5. Or
- Visit the test Page of the provided account via the following link:
[https://www.facebook.com/profile.php?id=61567383565480](https://www.facebook.com/profile.php?id=61567383565480)
3. **Step 3**: Click the **"Message"** button to open the chat feature and send a message to the Page.
4. **Step 4**: Send a message (e.g., "Hello") and wait for a response from the chatbot.
```

### pages_messaging

```shell
### Reason for Request:
- We are requesting the `pages_messaging` permission because it is essential for our service to support our Partner’s Facebook Pages in responding to customer inquiries.
- Our partners are business owners or shop managers who benefit from optimizing their resources through automated features such as scheduling posts, automatically responding to comments, and automatically replying to messages sent to their Facebook Pages.

### Details on how the `pages_messaging` permission is utilized within our service to enhance the customer experience:
- When our partners receive messages sent to their Facebook Page by customers:
- Our service processes the message content and sends an appropriate, automated response.
- This feature effectively addresses customer inquiries related to products or services, enhancing customer satisfaction and response time.

### Issue Noted During Previous Review:
- **Important**: It appears that during the previous review, the tester may not have used a Facebook account with **Tester role** in our App (App ID: `1054545482977612`).
- As our app is not yet public, it can only respond to messages from users with the **Tester** role or equivalent.
- Therefore, if the tester does not use an account assigned with the **Tester** role, the app will not respond to messages. This may have led to the bot not responding during the last review.
- We have updated your Facebook account (including email and password) to ensure you can log in normally.

### Note Before Testing This Feature:
- Please ensure you are using a Facebook account with **Tester role** in our app.
- If needed, you may use the following test Facebook account, which has already been added as a Tester:
- **Email**: khnh113a@gmail.com
- **Password**: Tuandenk56

### Steps to Test the Message Response Feature on Our App’s Page:
1. **Step 1**: Log in using a Facebook account with **Tester permissions** (use the test account provided above if necessary).
2. **Step 2**: Access the test Page via the following link:
[https://www.facebook.com/profile.php?id=100089894772702](https://www.facebook.com/profile.php?id=100089894772702)
3. **Step 3**: Click on the **"Message"** button to open the chat feature and send a message to the Page.
4. **Step 4**: Send a message (e.g., “Hello”) and wait for a response from the chatbot.

### Additional Information:
- The `pages_messaging` permission is vital to provide prompt and efficient responses to customers on behalf of our partners, reducing response times and enhancing customer satisfaction.
- This permission also allows businesses to optimize their workflow by automating responses, which can be crucial in handling high message volumes effectively.
```

### pages_show_list

```shell
### Reasons for Request:
- Our partners are businesses or store owners who wish to optimize their time and resources by scheduling posts automatically, auto-responding to Comments, and automatically replying to Messages sent to their Facebook Pages.
- We request the `pages_show_list` permission because this is necessary for our service to display the list of customers' Pages, allowing our customers to select the Page where they want our chatbot to respond to their customers on their Facebook Page.

### Details on How `pages_show_list` Permission is Used in Our Service to Enhance Customer Experience:
- Our partners connect their Facebook account and grant access permissions for their Pages.
=> We retrieve the list of Pages the customer has granted access to display on our interface (allowing customers to freely choose the Page they want to use with our services).
- This enhances customization for our partners, enabling them to quickly and intuitively browse and select Pages directly from our service's interface.
- This permission is essential because, without it, our customers would not be able to choose which Page to use the service with.

### Notes Before Testing This Feature:
- Please ensure you are using a Facebook account with the **Tester role** in our app.
- If needed, you may use the following test Facebook account, which has been added as a Tester:
  - **Email**: khnh113a@gmail.com
  - **Password**: Tuandenk56
- If you have problems with your 2FA code, use the **backup codes** below:
  - **Backup Code 1**: 2035 1061
  - **Backup Code 2**: 2366 5334
  - **Backup Code 3**: 3293 9232
  - **Backup Code 4**: 5191 0312
  - **Backup Code 5**: 5812 5637

### Issue Noted in the Previous Review:
- **Important**: It appears that in the previous review, the tester may not have used a Facebook account with the **Tester role** in our App (App ID: `1054545482977612`).
- Since our app is not yet public, it can only obtain an Access Token from users with the **Tester role** or equivalent for our related features when logging into Facebook.
- Therefore, if the tester does not use the designated account with the **Tester role**, the app will encounter an error as it still lacks the necessary permissions for public use with other users.
- We have checked the accounts, and they can log in correctly; we were unable to replicate the `experience looping` issue mentioned in your previous review. If you encounter this issue again, please describe in detail what happened so that we can follow up and resolve it.
- New video demo.
- We have provided additional recovery codes to ensure 2FA is passed.

### Steps to Test This Feature on Our App:
1. **Step 1**: Visit the URL: https://mekongai-social-media-bot.vercel.app

2. **Step 2**: Click "Sign In" on the MenuBar. Log in with the Test account details below:
   - **Username**: mekongai.dev.tester
   - **Password**: Mekongai@testing001
   => Click "Sign In."

3. **Step 3**:
   - Click the "Connect Facebook Account" button on the homepage.
   - Log in with your Facebook account. Please ensure you are using a Facebook account with the **Tester role** in our app. If needed, you may use the following test Facebook account, which has already been added as a Tester:
     - **Email**: khnh113a@gmail.com
     - **Password**: Tuandenk56
     - If you have problems with your 2FA code, use the backup codes below:
       - **Backup Code 1**: 2035 1061
       - **Backup Code 2**: 2366 5334
       - **Backup Code 3**: 3293 9232
       - **Backup Code 4**: 5191 0312
       - **Backup Code 5**: 5812 5637
   - In the "Select the Page you want MekongAI to access" section, choose "Apply to all current and future Pages" or "Grant access only to specific current news Pages" and click "Continue."
   - Click "Save" to confirm Page management permissions => "Understood."

4. **Step 4**: Click the "Dashboard" button on the MenuBar.

5. **Step 5**:
   - Click on "Message Manager" in the left menu.
   - In the Filter section, there is a "Select group/clan" Dropdown. Once clicked, it will display all Facebook accounts linked to the account along with the Pages granted access in Step 4.
   - You can select the desired Page for our chatbot to automatically respond to messages sent to their Page => Click the "Auto reply Message" button to apply.

### Steps to Test the Message Reply Feature on Our App Page:
1. **Step 1**: Log in with the Facebook account linked in Step 3 (use the provided test account if needed).
   - Visit the Website: https://facebook.com
   - Log in with your Facebook account. Please ensure you are using a Facebook account with the **Tester role** in our app. If needed, you may use the following test Facebook account, which has already been added as a Tester:
     - **Email**: khnh113a@gmail.com
     - **Password**: Tuandenk56
   - If you have problems with your 2FA code, use the backup codes below:
     - **Backup Code 1**: 2035 1061
     - **Backup Code 2**: 2366 5334
     - **Backup Code 3**: 3293 9232
     - **Backup Code 4**: 5191 0312
     - **Backup Code 5**: 5812 5637
     
2. **Step 2**:
   - Visit the Page registered with "Auto reply Message" in Step 5. Or
   - Visit the test Page of the provided account via the following link:
     [https://www.facebook.com/profile.php?id=61567383565480](https://www.facebook.com/profile.php?id=61567383565480)

3. **Step 3**: Click the **"Message"** button to open the chat feature and send a message to the Page.

4. **Step 4**: Send a message (e.g., "Hello") and wait for a response from the chatbot.

### Notes:
- The "Select group/clan" section allows users to precisely choose which Page they want our chatbot to automatically respond to messages sent to their Page. This enables customers to have more control over their experience with our service.
```

### pages_manage_metadata

```shell
### Reasons for Request:
- Our partners are businesses or store owners who wish to optimize their time and resources by scheduling posts automatically, **auto-responding to Comments**, and automatically replying to Messages sent to their Facebook Pages.
- We request the `pages_manage_metadata` permission because it is essential for our service to support our partners’ Facebook Pages in automatically responding to customer inquiries (auto-reply to comments).

### Details on how the `pages_manage_metadata` permission is utilized within our service to enhance the customer experience:
- When our partners receive comments sent to their Facebook Page posts by customers:
  - Our service processes the comments’ message content and sends an appropriate automated response.
  - This feature effectively addresses customer inquiries related to products or services, enhancing customer satisfaction and reducing response times.

### Steps to Test the Auto Reply Comments Response Feature on Our App’s Page:
1. **Step 1:** Access the test Page via the following link:  
   [https://www.facebook.com/mekongai.bot.socialmedia](https://www.facebook.com/mekongai.bot.socialmedia)
2. **Step 2:** Comment on any post on the accessed Page. For example, you can use this post:  
   [https://www.facebook.com/share/p/18QvATe73Z/](https://www.facebook.com/share/p/18QvATe73Z/)
3. **Step 3:** Wait for a response. The comment reply time will be approximately 30–60 seconds. You may need to refresh the page (F5) after that time to update the interface and view the reply.

### Additional Information:
- The `pages_messaging` permission is vital to provide prompt and efficient responses to customers on behalf of our partners, reducing response times and enhancing customer satisfaction.
- This permission also allows businesses to optimize their workflow by automating responses, which is crucial for handling high message volumes effectively.
```
