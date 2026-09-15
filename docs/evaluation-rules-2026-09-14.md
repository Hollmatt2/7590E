# Text-rule evaluation, 2026-09-14

Check set: 40 CUAD contracts, listed in `seed/check_set.txt`. Method: the text rules in `core/rules.py`, run on CUAD's own contract text split into clauses by `core/reading.py`. A flag counts as correct when it overlaps a clause the experts labeled for that category.

- **Recall**: of the labeled clauses, the share the rules flagged.
- **False-flag rate**: of the flags raised, the share that matched no labeled clause.

| Category | Labeled clauses | Found | Recall | Flags raised | Wrong | False-flag rate |
|---|---|---|---|---|---|---|
| Renewal Term | 21 | 14 | 67% | 27 | 13 | 48% |
| Notice Period To Terminate Renewal | 17 | 8 | 47% | 11 | 3 | 27% |
| Termination For Convenience | 30 | 10 | 33% | 37 | 27 | 73% |
| Anti-Assignment | 50 | 25 | 50% | 42 | 17 | 40% |
| Change Of Control | 30 | 19 | 63% | 52 | 30 | 58% |
| Governing Law | 40 | 32 | 80% | 81 | 49 | 60% |
| Audit Rights | 68 | 22 | 32% | 31 | 8 | 26% |
| Insurance | 61 | 25 | 41% | 37 | 8 | 22% |

No text rule (left for the AI model or a person): Cap On Liability, Uncapped Liability, Exclusivity, Warranty Duration.

The rules were written before this check set was chosen. Re-scoring a changed rule on the same contracts overstates how well it works.

## Examples

### Renewal Term

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Upon expiry of the Initial Term, this Agreement [*****] unless a Notice of non-renewal is given by either Party to the other Party [*****] prior to the expiry of the Initial Term or the end of a renewal period, if any.
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: Subject to the other provisions of this Agreement, the term of this Agreement shall commence on the Effective Date and shall remain in effect until terminated by either Party upon thirty (30) days' prior written notice.
- *FerroglobePlc_20150624_F-4A_EX-10.20_9154746_EX-10.20_Outsou*: It is established by calendar year and renewed tacitly every year.

Wrong flags (flagged, not labeled):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: 1.28 "Term" means the Initial Term and any and all Renewal Term(s) as set forth in Section 15.1 hereof.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Such LOC shall be renewed and its confirmation extended, at the latest [*****] before the expiry of each previous LOC;
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: 1.41 "Year" shall mean the twelve (12) months following the Supply Commencement Date and each successive twelve (12) month period commencing on the anniversary of the Supply Commencement Date.

### Notice Period To Terminate Renewal

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Upon expiry of the Initial Term, this Agreement [*****] unless a Notice of non-renewal is given by either Party to the other Party [*****] prior to the expiry of the Initial Term or the end of a renewal period, if any.
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: Following the Initial Term, the Agreement shall automatically be renewed for additional periods of **** (each, a "Renewal Term," and, together with the Initial Term, the "Term")), unless a Party provides written notification of non-renewal 
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: This Agreement is effective as of the Effective Date and will expire in accordance with Section 2.1, unless, upon the occurrence of any of the following events, this Agreement is earlier terminated in accordance with this Section 18.1: a) C

Wrong flags (flagged, not labeled):
- *MPLXLP_06_17_2015-EX-10.1-TRANSPORTATION SERVICES AGREEMENT*: If a Party advises in any Force Majeure Notice that it reasonably believes in good faith that the Force Majeure Period shall continue for more than twelve (12) consecutive months, then, subject to Section 10 below, at any time after a Party
- *AIRSPANNETWORKSINC_04_11_2000-EX-10.5-Distributor Agreement*: If Distributor wishes to extend the term of the Agreement beyond the Initial Term, it must notify Airspan in writing at least six (6) months prior to then end of the Initial Term.
- *LeadersonlineInc_20000427_S-1A_EX-10.8_4991089_EX-10.8_Co-Br*: To exercise this option, LeadersOnline must notify VerticalNet in writing of its election no later than 90 days prior to the expiration of the initial Term.

### Termination For Convenience

Missed (labeled, not flagged):
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Notwithstanding Section 7.1 above, this Agreement may be terminated upon the occurrence of any of the following events:
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: (d) By either party hereto upon sixty (60) days prior written notice to the other party hereto;
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: the receipt of such Notice by the Repairer or any other lesser period to be granted by the Repairer.

Wrong flags (flagged, not labeled):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: provided, however, that the foregoing will not apply to (y) any employee of the other party that responds to a public advertisement of employment opportunities or (z) any employee that was terminated without cause by the other party.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: 16.4 Termination procedure: to the fullest extent permitted by Law and/or under this Agreement, the termination of all or part of this Agreement, for any reason whatsoever, as per Clauses 3 ("Duration and renewal") and 16 ("Termination"), s
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: AZUL SA, F-1/A, 3/3/2017 Execution version CONFIDENTIAL TREATMENT REQUESTED Repairer may sustain and/or incur as a result of such termination 16.6.2 Mitigation In case of termination of all or part for any reason whatsoever and/or expiry of

### Anti-Assignment

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Consequently either this Agreement or any of the respective rights or obligations of the Parties hereunder may be assigned or otherwise transferred, in whole or in part, in any form whatsoever (including by way of change of Control), by eit
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: the Parties may at any time assign or transfer all or part of its rights and obligations under this Agreement to any of its Affiliates provided that such assignment or transfer is previously notified to the other Party.
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: Notwithstanding the aforesaid, either Party shall be entitled to assign, delegate, and/or subcontract its rights and obligation under this Agreement, in whole or in part, to one or more of its Affiliates on prior written notice to the other

Wrong flags (flagged, not labeled):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: The Beneficiary shall not be entitled to assign or transfer any right, title or interest in this StandBy Letter of Credit to any other party.
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: Customer shall be entitled to assign this Agreement, in whole or in part, to any person without the consent of Supplier, provided that (i) such person acquires all, or substantially all, of Customer's business or assets with respect to the 
- *HOLIDAYRVSUPERSTORESINC_04_15_2002-EX-10.13-ENDORSEMENT AGRE*: (ii) is the subject of any proceeding related to its liquidation or insolvency (whether voluntary or involuntary) which is not dismissed within ninety calendar days; (iii) makes an assignment for the benefit of creditors.

### Change Of Control

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: Notice of Merger or Acquisition. Until the date that this Agreement terminates or is terminated in accordance with Section 15 hereof, ENERGOUS agrees that, [***].
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Notwithstanding Section 7.1 above, this Agreement may be terminated upon the occurrence of any of the following events: (a) At the election of either party, in writing, if: (i) all or substantially all of the assets of the non-terminating p
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: or (v) the ownership or operations of the non-terminating party have materially changed;

Wrong flags (flagged, not labeled):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: 1.3 "Change of Control" means any transaction or series of transactions that results in (i) the consolidation or merger of the specified party ("Target") into or with any other corporation or corporations, (ii) the sale, conveyance or dispo
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: provided, however, that Change of Control will not include any transaction or series of transactions entered into primarily for equity financing purposes (including, without limitation, any private equity investment or any public offering o
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: provided, however, that "Product Updates" will only include any of the foregoing developed by an acquirer or successor of ENERGOUS for a period of [***] after a Change of Control of ENERGOUS, and provided further that any Products incorpora

### Governing Law

Missed (labeled, not flagged):
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: This Agreement is deemed made and entered into in the State of California and shall be construed, enforced and performed in accordance with the laws of the State of California, without reference, to choice of law.
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: This Agreement shall be interpreted and enforced exclusively under the laws of the State of Israel, without regard to the conflict of laws provisions thereof.
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: The laws of the State of New York (excluding any laws that direct the application of another jurisdiction's law) govern all matters arising out of or relating to this Agreement and all of the transactions it contemplates, including its vali

Wrong flags (flagged, not labeled):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: The licenses granted pursuant to this Agreement are license to rights in "intellectual property" (as that term is defined in Section 101 of the United States Bankruptcy Code) and governed by 11 USC Section 365(n).
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: THE RIGHTS AND OBLIGATIONS OF THE PARTIES IN CONNECTION WITH THIS AGREEMENT AND ANY PURCHASE OF THE PRODUCTS SHALL NOT BE GOVERNED BY THE PROVISIONS OF THE 1980 U.N.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: GOVERNING LAW AND ARBITRATION 37 AZUL-ATR Global Maintenance Master Agreement DS/CS-3957/14/Issue 7 Page 2/110 Source: AZUL SA, F-1/A, 3/3/2017 Execution version EXECUTION PAGE 39 EXHIBIT 1 - LIST OF ATR AIRCRAFT COVERED UNDER THIS AGREEMEN

### Audit Rights

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Company shall have the right, under EUR OPS or PART M equivalent applicable regulation approval, to audit the management and the performance of the Services provided by the Repairer under this Agreement, subject to giving a [*****] prior No
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: The cost of any such audits by the Company's representative(s) shall be borne by the Company unless if, as a result of that audit, the Repairer is found to be in Default, in which cases the cost of such audit will be borne by the Repairer.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Company's audit: at any time during the Term, the Repairer may: (i) audit the management and the performance of the Company's maintenance activities which are still under Company'sresponsibility; and/or, (ii) arrange for operational visits,

Wrong flags (flagged, not labeled):
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: EKR shall during business hours, on no less than 14 day's notice from PPI and not more than once in any Calendar Year, make available for inspection the records and books referred to in Section 7.2.
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: 3.31 Records and Audits (a) Vendor shall maintain complete and accurate records relating to the Work and the performance of this Agreement.
- *AimmuneTherapeuticsInc_20200205_8-K_EX-10.3_11967170_EX-10.3*: Records; Audits 24 ARTICLE 9 Intellectual Property Matters 26

### Insurance

Missed (labeled, not flagged):
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Both Parties will each have and maintain in full force and effect during the Term of this Agreement (including any post-termination period for which indemnification obligations continue), all product liability and other insurance reasonably
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Such policy or policies will (a) have aggregate limits of liability of not less than $1,000,000 with respect to any incident or occurrence and of not less than $2,000,000 in the aggregate; (b) name both Zanotti and Aura as insured parties; 
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Without prejudice to any term and condition under this Agreement, the Company shall maintain in force, at all times during the Term and [*****], at its own costs and expenses, with insurers of internationally recognized

Wrong flags (flagged, not labeled):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: The Company also agrees to promptly pay each premium in respect of the aforesaid insurances and in the event of its failure to take out or maintain any such insurance then, without prejudice to any other rights it may have in respect of suc
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: Article 15 Insurance 35 15.1 Insurance Coverage 35 15.2 Evidence of Insurance 35
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: Vendor shall procure all approvals, bonds, certificates, insurance, inspections, licenses, and permits that such Laws require for the performance of this Agreement.
