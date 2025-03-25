# Add a test script to the "Create Idea" request to automatically save the ideaId:
```js
var jsonData = JSON.parse(responseBody);
pm.environment.set("ideaId", jsonData.ideaId);
```

# Add error handling tests:
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    var jsonData = JSON.parse(responseBody);
    pm.expect(jsonData).to.have.property('ideaId');
    pm.expect(jsonData).to.have.property('message');
});
```

# Add pre-request scripts to check for required environment variables:
```js
if (!pm.environment.get("authToken")) {
    throw new Error("Authentication token is required. Please run the Sign In request first.");
}
```
