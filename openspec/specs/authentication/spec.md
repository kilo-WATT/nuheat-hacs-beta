# Authentication

## Purpose
Preserve working OAuth provider associations while supporting community beta sign-in and legitimate custom application credentials.

## Requirements

### Requirement: Explicit provider selection
The beta SHALL register its community provider alongside stored NuHeat Application Credentials. Multiple providers SHALL be presented recognizably; an existing OAuth entry SHALL retain its associated provider. Stored custom credentials SHALL NOT be deleted or silently replaced.

#### Scenario: Existing custom credentials
- **WHEN** a user has a legitimate custom OAuth application
- **THEN** it remains selectable and existing entries retain their association.

### Requirement: Community callback prerequisite
The beta's community provider SHALL require the My integration before starting authorization and explain its absence. It SHALL use the validated My callback rather than silently substitute an unsupported direct redirect. Custom applications SHALL retain their own standard callback behavior.

#### Scenario: My integration is disabled
- **WHEN** community sign-in is requested without My loaded
- **THEN** setup explains how to enable it without automatically editing HA configuration.

#### Scenario: Custom provider without My
- **WHEN** a custom application supports a direct callback and My is absent
- **THEN** it is not forced onto the community provider or community callback.

### Requirement: OAuth verification and privacy
OAuth SHALL retain S256 PKCE, refresh-token handling, and account ownership validation. Tests and planning artifacts SHALL use synthetic credentials and identifiers. Shared beta registration values SHALL NOT be copied into Core, the client library, or specification files.

#### Scenario: Authorization failure
- **WHEN** authorization or token exchange fails
- **THEN** no success or account ownership is invented and diagnostic requests avoid passwords, tokens, callback URLs, and serial numbers.
