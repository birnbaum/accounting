# Environmental Accounting in Cloud and Accelerator Providers

# Environmental Accounting

Differentiate! Not interchangable!

**Corporate-level sustainability disclosures**

energy, emissions, water, waste and verification at the company boundary

**Customer-facing**

workload or service-level accounting tools intended to support customers’ Scope 3 reporting and decision-making

## Carbon reporting

Most of the big providers do, but different.

### **System Boundaries**

### GHG Protocol

### Scope 2 Guidance: https://ghgprotocol.org/sites/default/files/2023-03/Scope%202%20Guidance.pdf

TODO: Revision

### Scope 3 Guidance: https://ghgprotocol.org/sites/default/files/standards/Scope3_Calculation_Guidance_0.pdf?utm_source=chatgpt.com

→ Scope 1-3 for cloud providers become Scope 3 Category 1 (Purchased goods and services) for customers

![image.png](Environmental%20Accounting%20in%20Cloud%20and%20Accelerator%20/image.png)

### **LBM vs. MBM**

The GHG requires both for Scope 2:

- **Location-based method**: What are the emissions physically associated with the electricity I use? Usually average carbon intensity → Physical grid reality and real climate impact
- **Market-based method**: What emissions are associated with the electricity I contractually chose to buy?  e.g. PPAs, RECs, GoOs → Economic incentives and investment signals

## Energy reporting

- Google: “Energy consumption associated with each customer's usage is available for customers participating in a private preview.”
- Oracle promotes power-based calculation but does **not** report power
- **Problem**
    - They don’t need to in order to comply with GHG Protocol Scope 2
    - Carbon is more “abstract” (energy is more disputable methodology-wise due to shared servers with multi-tenant workloads, static vs dynamic power, overhead allocation, …)
    - Power might expose sensitive information
    - Auditors might demand assurance, errors are financial risks
    - They don’t want you to think about the fact that servers consume energy
- AWS even has an article on reverse engineering, which avoids accountability “this method is for informational purposes only” https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-energy.html?utm_source=chatgpt.com

## Water Reporting

Very rare and less standardized. Corporate reporting often uses withdrawals, discharges and “water positive” replenishment programmes. Facilities can report [WUE (water usage effectiveness).](https://www.notion.so/Environmental-Accounting-in-Cloud-and-Accelerator-Providers-2f5072369aef80f48d40c42fecb8eafd?pvs=21)

Customer-facing water reporting:

- Only scaleway reports water as: electricity consumption x WUE

## Definitions

Besides GHG, LBM/MBM, LCA

- **Activity data**: quantitative measure that models of a level of activity that results in GHG Emissions during a given period of time (e.g., amount of diesel consumed, gigabytes of storage used, dollars spent, etc.).
- **Allocation**: The action of apportioning emissions of a given activity to a product/service/other activity based on an established weighting factor: e.g., usage-based (‘physical allocation’) or equivalent revenue-based (‘economic allocation’).
- **Amortization**: The process of normalizing non-operational emissions of cloud services. E.g. embodied carbon in server racks measured in kgCO2e per rack, amortized over the rack’s lifetime, and converted into monthly emissions to be allocated to customers.
- **PPD**: Planned Power Draw. The expected average power draw during peak usage conditions for a given server rack. The primary purpose of PPD values is to drive planning decisions to reserve sufficient power for each server rack deployed in data centers.
- **Operational emissions**: Scope 1, 2, and Scope 3 FERA (for DCs sometimes only Scope 2)
- **Embodied/Capital emissions**: Rest of Scope 3
- **Emission factor / carbon intensity**: Coefficient that quantifies the emissions released froma given activity (e.g. production of 1 kWh of electricity).
- **EACs**: Energy Attribute Certificates serve as an instrument to represent exclusive rights to the environmental, social, and other non-power attributes of renewable generation.
    - generally equate to one certificate for each 1 MWh of renewable energy produced by a renewable energy project
    - can be utilized to reduce Scope 2 emissions under the market-based method (MBM) if generated and allocated within the same GHG defined boundary
    - called RECs (Renewable Energy Certificates) in the US and GOs (Guarantees of Origin) in the EU
- **PPA**: Power Purchase Agreement is a long-term contract between an electricity generator and an electricitycustomer to supply a certain amount of electricity at a pre-negotiated price (either fixed or indexed).PPA terms can vary in duration.
- **Residual grid mix:** The carbon intensity left after EACs, PPAs, and supplier-specific emission rates are removed from the system.
- **Equivalent revenue:** weighting factor leveraged when applying *economic allocation*. It is a standardized measure of usage-based revenue that excludes pricing variation factors such as discounts, and other adjustments. It reflects service usage for each customer account, allowing for consistent comparison across customer segments, time periods and regions.

AWS

- **Foundational service (FS)**: AWS services that have dedicated server racks in AWS data centers.
- **Non-foundational service (nFS)**: AWS services with no dedicated server racks, which rely on foundational services to providefunctionality to end customers.
- **MEC**: Month End Close: An operational monthly process that AWS takes to release updated carbon footprint data.
- **Cluster-level carbon footprint:** Footprint of a single cluster / cloud region
- **Customer-segment-level carbon footprint**: carbon footprint for a particular group of customers that are using a specific service
- **Service-level carbon footprint:** This can be a footprint for a foundational or a non-foundational AWS service in any given cluster.

# Provider Analysis

## AWS

- Customer Carbon Footprint Tool (CCFT) (currently Model 3.0): https://aws.amazon.com/sustainability/tools/aws-customer-carbon-footprint-tool/
- Methodology: [https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology.pdf](https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology.pdf)

Quantifies customer-specific GHG emissions associated with the use of AWS cloud services (EC2, S3, Lambda, Sagemaker, …)

- Based on GHG Protocol and LCA
- accounted on a monthly basis for the previous 38 months
    - broken down by AWS Region
    - and by service
- Recasting of at least one year in case of significant methodology updates

### System Boundaries

- **Scope 1** – direct emissions from AWS operations (fuel combustion in emergency back-upgenerators, gas power plants, …)
    - **Excludes** (non-attributable): Fleet vehicles
    - **Excludes** (non-attributable): Facilities beyond data centers, such as warehouses, offices, or sites run in customer facilities
- **Scope 2** – indirect emissions from purchased energy
    - **Excludes** (non-attributable): Facilities beyond data centers, such as warehouses, offices, or sites run in customer facilities
- **Scope 3**:
    - **Included operational emissions** (not included in Scope 1 & 2):
        - FERA (Fuel & Energy Related Activities): [https://ghgprotocol.org/sites/default/files/2022-12/Chapter3.pdf](https://ghgprotocol.org/sites/default/files/2022-12/Chapter3.pdf) — E.g. upstream emissions of purchased fuels and electricity; T&D losses
    - **Included capital emissions:**
        - Embodied carbon of IT hardware (cradle-to-gate: extraction of raw materials, manufacturing of components, assembly, transportation)
        - Embodied carbon of non-IT equipment (e.g., generators, air handling units, etc.) (cradle-to-gate)
        - Embodied carbon of data center buildings (cradle-to-gate)
        - Emissions from upstream transport and distribution (e.g., emission arising from transporting server racks to the data center sites).
    - **Excludes** (non-attributable): Facilities beyond data centers, such as warehouses, offices, or sites run in customer facilities
    - **Excludes**: End-of-life of IT hardware, non-IT equipment, and data center buildings

### Input Data

<aside>
⚠️

We prioritize quality of data at the time of publishing CCF data, falling back to other sources (e.g. estimated load) when the primary source of data (e.g. actual load from power invoices) is not reasonably available. We correct our estimates when recasting, to align emissions reported in the CCF model with the assured data.

- The load data is estimated from utility power invoices, historical data – e.g., deployed power – and forecasted data – e.g., planned server racks and YoY growth rate estimates. The ‘composition’ of the load data changes over time, based on how timely the data sources (e.g., power invoices) are available for the sites in scope.
- timing lag between EAC creation, delivery, and retirement, we estimate EACs

**Finding:** This stuff is not real time at all

</aside>

**Scope 2**

Load := Estimate Load at cluster-month level

EACs := Allocate EACs at a cluster-month level based on local load, grid mix (% renewables), estimated EACs

ef_LBM := average carbon intensity

ef_MBM := residual mix emission factors

- LBM: Load * ef_LBM
- MBM: (Load - EACs) * ef_MBM + EACs * ef_EACs

**Scope 3**

- Fuel and Energy Related Activities (FERA) methodology similar as Scope 2

Emboddied Carbon in IT Hardware:

![image.png](Environmental%20Accounting%20in%20Cloud%20and%20Accelerator%20/image%201.png)

Rest not reviewed in detail

### Allocation

Monthly basis on *physical allocation* – i.e., usage-based allocation

- considers *economic allocation* – i.e.,based on equivalent revenue – as a fall-back option.

Flow:

- 

Faster publishing time
Monthly carbon estimates are now published by the 21st of the month after the usage occurs. For example, November carbon estimates are published by December 21st.

• top-down allocation model: allocate cluster emissions to racks; racks to services (physical allocation where dedicated, economic allocation otherwise); then allocate services to customer accounts
• independently verified

Energy: No, but [AWS Billing Calculating your energy usage - AWS Billing](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-energy.html?utm_source=chatgpt.com)

|  | Carbon | Energy | Water | Source |
| --- | --- | --- | --- | --- |
| **AWS model 3.0**
Customer Carbon Footprint Tool (CCFT) |   •  | No, but https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-energy.html?utm_source=chatgpt.com | No | https://aws.amazon.com/sustainability/tools/aws-customer-carbon-footprint-tool/ |
| **Google Cloud**
 |   • **not** third-party verified
  • both location-based and market-based broken down by project, product, and region, with monthly data availability
  • Uses hourly grid intensity
  • TODO Check LCA | only available to customers in a private preview | No | https://docs.cloud.google.com/carbon-footprint/docs/methodology |
| **Microsoft Azure**
Emissions Impact Dashboard |   • Scopes 1, 2, and 3, third-party verified | No | No | https://www.microsoft.com/en-us/sustainability/emissions-impact-dashboard |

- AWS model 3.0
    - AWS CustomerCarbonFootprintMethodology: https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology.pdf
    - 
- Microsoft Emissions Impact Dashboard (Scope 1-3, life cycle framing and customer allocation model)
    - Emissions Impact Dashboard for Azure: https://marketplace.microsoft.com/en-au/product/power-bi/coi-sustainability.emissions_impact_dashboard
    - 2024 Environmental Sustainability Report http://cdn-dynmedia-1.microsoft.com/
- Google Cloud Carbon Footprint (Scope 1-3, hourly location-based modelling and annual market-based scaling, third-party review letter)
    - https://docs.cloud.google.com/carbon-footprint/docs/methodology
        - Google does calculate customer-level energy consumption (kWh) and allocates machine-level power use down to internal services and then to customers
        - “Energy consumption associated with each customer's usage is available for customers participating in a private preview.”
- Oracle OCI Carbon Emissions Analysis (power-based and spend-based methods; location-based and market-based factors; explicit “estimate” disclaimers)
    - Technical Carbon Calculation Guidance to Support Customer Requests on Sustainability Reporting: https://www.oracle.com/a/ocom/docs/corporate/technical-carbon-calculation-guidance.pdf
    - https://docs.oracle.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm?utm_source=chatgpt.com
    - https://blogs.oracle.com/cloud-infrastructure/oci-carbon-emissions-power-based-calculations
    
- IBM Cloud Carbon Calculator (operational only; explicit exclusions of embodied emissions; PUE sourced from colocation landlords)
    - IBM Cloud Carbon Calculator (energy & carbon quantification methodology): [cloud.ibm.com](http://cloud.ibm.com/)
- Scaleway explicitly provides both carbon and water consumption with daily-updated metrics and downloadable reports
    - https://www.scaleway.com/en/environmental-footprint-calculator/
    - https://www.scaleway.com/en/docs/environmental-footprint/how-to/track-monthly-footprint/
- OVHcloud
    - OVHcloud Environmental Impact Tracker Methodology: https://corporate.ovhcloud.com/sites/default/files/2025-07/environmental_impact_tracker_-_methodology.pdf
- NEO: Equinix
    - https://docs.equinix.com/observability/sustainability/ecp-sustainability/
    - https://sustainability.equinix.com/
- NEO: CoreWeave: public statements about sites powered by renewable energy, but no customer emissions or energy accounting tool https://www.coreweave.com/news/coreweave-announces-two-initial-data-centers-in-the-uk-are-now-operational?utm_source=chatgpt.com
- NEO: Lambda: public sustainability-adjacent announcements (example: hydrogen-powered deployment), but no customer emissions or energy accounting tool https://lambda.ai/blog/lambda-ecl-bring-first-hydrogen-powered-nvidia-gb300-nvl72-systems-online?utm_source=chatgpt.com

## Google

- In-context “low-CO2” selector

## External validation

- AWS provides a limited assurance statement scoped to methodology validation of select Scope 3 elements https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf
- Google publishes a third-party review letter that explicitly states it is not a verification or assurance engagement
- Equinix reports external verification of its corporate energy and emissions data under limited assurance.

## Best practices

Verify!

- publishing the full allocation model and its fallbacks (AWS)
- disclosing market-based versus location-based logic and update cadence (Google, Oracle)
- distinguishing operational versus embodied components and amortising embodied impacts over asset life (AWS, Microsoft, OVHcloud)
- extending customer tools beyond carbon (Scaleway, OVHcloud).

## Neo-cloud Providers

The largest gap for accelerator-focused and “neo GPU” providers is the absence of standardised, customer-level environmental accounting documentation.

- if in colocation / leased facilities, environmental transparency depends on the underlying datacentre operator’s reporting (for example, Equinix provides customer-allocated electricity and emissions for colocation customers).

# Common weaknesses

- **Boundary** and scope coverage vary (Scope 1/2 only vs adding parts of Scope 3; what is included in embodied hardware, buildings, networking)
- **Allocation** is under-explained (how shared infrastructure, cooling, networking, and overheads are attributed to a given customer or workload).
- **Market-based vs location-based** Scope 2 can be gamed or misunderstood if presented without context and dual reporting.
- **Temporal and geographic granularity** (hourly vs annual averaging; region-level assumptions)
- **Verification and reproducibility**: dashboards rarely let customers independently recompute from first principles because key inputs (exact energy models, PUE assumptions, residual mix factors, procurement matching rules) are not fully exposed

# Regulation: CSRD

 https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en

Difference to cloud carbon dashboards:

- Double materiality
    - Impact materiality: How their activities affect climate and the environment.
    - Financial materiality: How climate risks and transition dynamics affect their financial performance.
- Full Scope 1, 2 (both location-based and market-based) and 3 coverage
- Auditability
    - Clear system boundaries
    - Transparent allocation rules
    - Reproducible methodologies
    - Documented data sources
    - Versioning and traceability
- Standardization: Required metrics, Required methodologies or methodological references, Disclosure structure, Digital tagging for machine readability.

# Regulation: ISO

- ISO 14064-1: [https://www.iso.org/standard/66453.html](https://www.iso.org/standard/66453.html) Greenhouse gases — Part 1: Specification with guidance at the organization level for quantification and reporting of greenhouse gas emissions and removals
- ISO 14040: Environmental management — Life cycle assessment — Principles and framework
- ISO 14044: Environmental management — Life cycle assessment — Requirements and guidelines

# Papers / Reports

- https://dl.acm.org/doi/10.1145/3604930.3605721
- [Maybe trash]Towards Sustainable Cloud Computing: A Comparative Evaluation
of Carbon Footprint Calculator Tools: [www.scitepress.org](http://www.scitepress.org/)
- [GREENS’25, Accenture] Calculating Software’s Energy Use and Carbon Emissions: A Survey of the State of Art, Challenges, and the Way Ahead: https://arxiv.org/pdf/2506.09683v1
- EBU Technical Review (2025) on “Cloud Energy Use Tools”: https://tech.ebu.ch/files/live/sites/tech/files/shared/techreview/trev_2025-02_Cloud_energy_use_tools.pdf
- Boavitza 2023: Understanding the results of cloud providers' carbon calculators: https://web.archive.org/web/20251206060724/https://boavizta.org/en/blog/calculettes-carbone-clouds-providers
- One Token Model

# Cite

- [https://spectrum.ieee.org/data-center-sustainability-metrics](https://spectrum.ieee.org/data-center-sustainability-metrics)
- [https://dl.acm.org/doi/pdf/10.1145/3630614.3630627](https://dl.acm.org/doi/pdf/10.1145/3630614.3630627)
- [https://www.deloitte.com/uk/en/issues/climate/addressing-the-disconnect-in-carbon-accounting-and-reporting-in-the-built-environment.html](https://www.deloitte.com/uk/en/issues/climate/addressing-the-disconnect-in-carbon-accounting-and-reporting-in-the-built-environment.html)

## WUE and Cooling

https://blog.equinix.com/blog/2024/11/13/what-is-water-usage-effectiveness-wue-in-data-centers/

[https://www.youtube.com/watch?v=JYmu1eNvfNQ](https://www.youtube.com/watch?v=JYmu1eNvfNQ)

### WUE

Cubic meters of water per megawatt hour of energy (m3/MWh)

- Facility that uses no water: WUE=0
- Facility that uses evaporative cooling exclusively could report a WUE as high as 2.5
- In practice: WUE varies over the year, e.g. DCs often use air cooling only during winter

![image.png](Environmental%20Accounting%20in%20Cloud%20and%20Accelerator%20/3ec1fdac-a292-4f40-a374-289f848d2c08.png)

Careful: Using air cooling instead of evaporative cooling will decrease WUE, but increase PUE

# Links

- https://www.linkedin.com/posts/david-younan-montgomery_i-just-submitted-a-formal-complaint-to-the-activity-7421595677748805632-dVg2?utm_source=share&utm_medium=member_ios&rcm=ACoAABnuOPUB8AgTIGA694DK8btrWUrIfxmnzZQ
- https://www.linkedin.com/posts/electricitymaps_electricity-maps-ghgp-scope-2-public-consultation-activity-7421890843202023424-eqU2?utm_source=share&utm_medium=member_ios&rcm=ACoAABnuOPUB8AgTIGA694DK8btrWUrIfxmnzZQ
- https://www.linkedin.com/posts/gillenwater_what-is-ghg-accounting-market-based-approaches-activity-7423103067602046976-pQlC?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAABnuOPUB8AgTIGA694DK8btrWUrIfxmnzZQ
- Watttime additionality complaint: https://watttime.org/wp-content/uploads/2026/01/Scientific-Accuracy-Additionality-Complaint-1.6.26.pdf

- https://www.linkedin.com/posts/alex-iacob-898775194_two-papers-accepted-at-iclr-2026-ugcPost-7421899253163225088-LP4u?utm_source=share&utm_medium=member_ios&rcm=ACoAABnuOPUB8AgTIGA694DK8btrWUrIfxmnzZQ

https://hal.science/hal-05512793/document

https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6219838&ct=t(EMAIL_CAMPAIGN_2026-FEBRUARY-20-175)

NREL:

- [https://www.pnas.org/doi/10.1073/pnas.2211624119](https://www.pnas.org/doi/10.1073/pnas.2211624119)
- No composite: does not exist, or will ever
- average emissions are a good heuristic

- Create accounts on all platforms
- Guide for users → here is what you should know about it

# Conclusions

→ We need comparability

→ We need more real-time accounting to enable optimization

→ We need uncertainty quantification over time to judge if optimization is even meaningful

→ We need transparency or at least verifiability

The GHG protocol is the gold standard, but it leaves many things a bit vague on opaque

- We should understand where cloud providers definitely diverge, but also where they simply differently interpret under-specified or ambiguous parts of the GHG protocol

- Presentation and transparency!
