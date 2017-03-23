This wrapper does the following:

- Load the ca.dll with LoadLibrary
- Re-export the ca API and dynamically route the call back to ca.dll.
- On detach, don't call FreeLibrary to ca.dll


