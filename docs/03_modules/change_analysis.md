# Change Impact Analysis Module

This module predicts the downstream impact of proposed changes before deployment.

---

## Inputs
- Pull request diff
- Schema change
- Configuration change

---

## Analysis Steps

1. Identify affected components
2. Traverse downstream dependencies
3. Compute blast radius
4. Evaluate historical incident correlation
5. Assign risk score
6. Generate explainable summary

---

## Comparison Model

- Feature branch is compared only against main
- No branch-to-branch comparison
- No analysis of unstable local branches

---

## Outputs
- Impacted services and components
- Risk score
- Explanation with supporting evidence
- Confidence level