# Privacy policy

This plugin processes a user-supplied career master YAML, job descriptions, and
application manifests. When the user explicitly invokes **Save career memory**, a
validated copy is stored in the current Dify workspace's plugin key-value storage.
Email, phone, street-address, and birth-date fields are replaced by redacted values by
default. The user can opt into contact storage through a form setting intended only
for trusted self-hosted deployments. Generated job context never includes contact.

The plugin does not send data to an external service by itself. The surrounding Dify
application and selected model provider may still receive tool inputs and outputs.
Use a self-hosted Dify deployment or a provider whose data policy is acceptable for
personal information. Names, locations, claims, evidence titles, JDs, and manifests
remain personal data even with contact redaction. Never store contracts, identity
documents, credentials, private keys, or server topology in career memory.

Deleting or uninstalling the plugin may be required to remove workspace storage,
depending on the Dify deployment. Consult the deployment administrator before using
this plugin for another person.
