# AI evaluation, 2026-09-17

Check set: 40 CUAD contracts from `seed/check_set.txt`, split into clauses by `core/reading.py`. A flag counts as correct when it overlaps a clause the experts labeled for that category. Recall: of the labeled clauses, the share flagged. False-flag rate: of the flags raised, the share that matched no labeled clause.

Method: the AI step in `core/ai_identify.py`, model `claude-haiku-4-5`, all findings. Tokens: 647,998 input, 0 cache write, 0 cache read, 46,291 output; cost about $0.88.

| Category | Labeled clauses | Found | Recall | Flags raised | Wrong | False-flag rate |
|---|---|---|---|---|---|---|
| Cap On Liability | 69 | 33 | 48% | 46 | 13 | 28% |
| Uncapped Liability | 23 | 6 | 26% | 24 | 18 | 75% |
| Renewal Term | 21 | 18 | 86% | 24 | 6 | 25% |
| Notice Period To Terminate Renewal | 17 | 15 | 88% | 21 | 5 | 24% |
| Termination For Convenience | 30 | 18 | 60% | 32 | 14 | 44% |
| Anti-Assignment | 50 | 31 | 62% | 33 | 3 | 9% |
| Change Of Control | 30 | 18 | 60% | 25 | 8 | 32% |
| Governing Law | 40 | 36 | 90% | 38 | 2 | 5% |
| Exclusivity | 27 | 14 | 52% | 26 | 12 | 46% |
| Audit Rights | 68 | 22 | 32% | 29 | 7 | 24% |
| Insurance | 61 | 16 | 26% | 15 | 2 | 13% |
| Warranty Duration | 19 | 7 | 37% | 21 | 14 | 67% |

## At different confidence thresholds

Findings below the threshold are ignored. For the threshold note (brief, section 6.4).

| Category | Recall ≥0.5 | False flags ≥0.5 | Recall ≥0.7 | False flags ≥0.7 | Recall ≥0.9 | False flags ≥0.9 |
|---|---|---|---|---|---|---|
| Cap On Liability | 48% | 28% | 48% | 27% | 38% | 4% |
| Uncapped Liability | 26% | 74% | 26% | 74% | 22% | 55% |
| Renewal Term | 81% | 15% | 81% | 11% | 71% | 0% |
| Notice Period To Terminate Renewal | 88% | 20% | 82% | 17% | 82% | 6% |
| Termination For Convenience | 60% | 40% | 60% | 38% | 60% | 18% |
| Anti-Assignment | 62% | 9% | 62% | 9% | 58% | 3% |
| Change Of Control | 60% | 29% | 60% | 29% | 50% | 12% |
| Governing Law | 90% | 5% | 90% | 0% | 90% | 0% |
| Exclusivity | 52% | 46% | 52% | 42% | 48% | 38% |
| Audit Rights | 32% | 24% | 32% | 19% | 29% | 9% |
| Insurance | 26% | 7% | 25% | 8% | 25% | 0% |
| Warranty Duration | 37% | 56% | 37% | 22% | 26% | 0% |

## Examples

### Cap On Liability

Missed (labeled, not flagged):
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: NEITHER PARTY SHALL NOT BE LIABLE TO THE OTHER FOR ANY DAMAGES, LOSSES OR EXPENSES RESULTING FROM ANY TERMINATION OR EXPIRATION OF THIS AGREEMENT ARISING FROM ANY CLAIMS ASSERTED WHICH ARE BASED UPON LOSS OF GOODWILL, PROSPECTIVE PROFITS OR
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: Dexcel's responsibility for Product supplied by it to Kitov failing to meet the Specifications shall be limited to the replacement of the Product or the refund of the Supply Price paid by Kitov for such order, as agreed by the parties, exce
- *NANOPHASETECHNOLOGIESCORP_11_01_2005-EX-99.1-DISTRIBUTOR AGR*: SELLER EXPRESSLY DISCLAIMS ANY AND ALL LIABILITY TO BUYER FOR ANY CONSEQUENTIAL DAMAGES, DAMAGES FOR LOSS OF USE, LOSS OF PROFITS, INCOME, OR REVENUE, LOSS OF TIME OR INCONVENIENCE, LOSS OR DAMAGE TO ASSOCIATED EQUIPMENT, COST OF SUBSTITUTE

Wrong flags (flagged, not labeled):
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: If Vendor is the Party whose performance is prevented or delayed by a Force Majeure Event and AT&T determines that the Force Majeure Event is reasonably likely to cause a material delay of the ultimate Delivery Date or Completion Date for a
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: provided, however, that if Vendor has not cured all such non- conformance with respect to the Cell Site within nine (9) months following Provisional Location Acceptance (or sixty (60) days if the non-conformance is caused by the existence o
- *NeuroboPharmaceuticalsInc_20190903_S-4_EX-10.36_11802165_EX-*: Articles or Sections 8.2 (Limitation of Liability), 9 (Indemnification), 12.2 (Force Majeure), 12.3 (Assignment), 12.4 (Severability), 12.6 (Remedies), 12.8 (Submission to Jurisdiction/Waiver of Jury Trial), 12.9 (Independent Contractor/No 

### Uncapped Liability

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: EXCEPT IN THE CASE OF (a) ANY BREACH OF SECTION 10 (CONFIDENTIALITY), (b) THE PARTIES' OBLIGATIONS UNDER SECTION 12 (INDEMNIFICATION), (c) A PARTY'S GROSS NEGLIGENCE OR WILLFUL MISCONDUCT, OR (d) LIABILITY ARISING FROM EPIDEMIC DEFECTS (WHI
- *NANOPHASETECHNOLOGIESCORP_11_01_2005-EX-99.1-DISTRIBUTOR AGR*: Buyer, for itself and its insurers, expressly waives any and all limitations or liability caps, if any, on Buyer's contribution liability to Seller, and any and all statutory or common law lien rights or Claims against Seller arising from a
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: Any and all liability of PPI to EKR howsoever arising in respect of this Agreement, the Transition Services and Inventory Agreement or the Supply Agreement and their performance, in contract tort or otherwise, shall be limited (except for d

Wrong flags (flagged, not labeled):
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: Notwithstanding any other provisions of this Agreement, PPI will defend, indemnify and hold harmless the EKR Infringement Indemnitees from and against all liabilities, losses, damages, actions, claims and expenses suffered or incurred by th
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: PPI shall be liable for and shall defend, indemnify and hold harmless EKR and its Affiliates and their officers, directors, agents, representatives, consultants and employees (individually an "EKR Indemnified Party" and collectively the "EK
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: PPI shall pay all costs and expenses of the filing, prosecution and maintenance of the PPI Patents in each country of the Territory so as to maintain the PPI Patents in full force and effect.

### Renewal Term

Missed (labeled, not flagged):
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: Subject to the other provisions of this Agreement, the term of this Agreement shall commence on the Effective Date and shall remain in effect until terminated by either Party upon thirty (30) days' prior written notice.
- *NOVOINTEGRATEDSCIENCES,INC_12_23_2019-EX-10.1-JOINT VENTURE *: It is understood that a subsequent renewal of a five (5) year term will be negotiated in good faith and shall carry terms very close to the original Agreement.
- *LeadersonlineInc_20000427_S-1A_EX-10.8_4991089_EX-10.8_Co-Br*: LeadersOnline shall have the option, subject to VerticalNet's approval exercised in its sole and absolute discretion, to extend the Term of this Agreement for an additional 12 months (a "Renewal Term") on such terms and conditions as may be

Wrong flags (flagged, not labeled):
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: The "Term" of this Agreement shall commence on the Effective Date and shall continue in full force and effect until the expiration or earlier termination of the last Addendum to expire or be terminated, at which time this Agreement will exp
- *NeuroboPharmaceuticalsInc_20190903_S-4_EX-10.36_11802165_EX-*: This Agreement shall commence on the Effective Date and, unless earlier terminated, shall continue in full force and effect for a period of [***] years thereafter.
- *VerizonAbsLlc_20200123_8-K_EX-10.4_11952335_EX-10.4_Service *: This Agreement will terminate on the earlier to occur of (a) the date upon which the last remaining Receivable is paid in full, settled, sold or written off and any amounts received are applied and (b) the Issuer is terminated under Section

### Notice Period To Terminate Renewal

Missed (labeled, not flagged):
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: Subject to the other provisions of this Agreement, the term of this Agreement shall commence on the Effective Date and shall remain in effect until terminated by either Party upon thirty (30) days' prior written notice.
- *FerroglobePlc_20150624_F-4A_EX-10.20_9154746_EX-10.20_Outsou*: The Agreement rests, for all that, cancellable at any time by any of the parties before the expiry date of the Agreement or any of itsrenewals, upon three months prior written notice.

Wrong flags (flagged, not labeled):
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: The "Term" of this Agreement shall commence on the Effective Date and shall continue in full force and effect until the expiration or earlier termination of the last Addendum to expire or be terminated, at which time this Agreement will exp
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: If either Transporter or Shipper is rendered unable by an event of Force Majeure to carry out, in whole or part, its obligations hereunder and such Party gives notice and full details of the event to the other Party as soon as practicable a
- *MERITLIFEINSURANCECO_06_19_2020-EX-10.(XIV)-MASTER SERVICES *: At any time that there is no uncompleted Statement of Work outstanding, either party may terminate this Agreement for any or no reason upon fifteen (15) days advance notice to the other.

### Termination For Convenience

Missed (labeled, not flagged):
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Notwithstanding Section 7.1 above, this Agreement may be terminated upon the occurrence of any of the following events:
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Early termination fee: subject to not being in breach of any of its obligation under the Agreement, the Company may terminate this Agreement for convenience by way of Notice of termination; the Agreement shall be then terminated following a
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: the receipt of such Notice by the Repairer or any other lesser period to be granted by the Repairer.

Wrong flags (flagged, not labeled):
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: In the event that the Parties are unable to agree on such an arrangement, either Party shall be entitled to provide immediate written notice of termination to the other Party.
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: Customer delivers written notice of termination to Supplier at least [* * *] prior to the expiration date of the Initial Term, which termination shall be effective as of the expiration date of the Initial Term
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: either Party delivers written notice of termination to the other Party at least [* * *] prior to the expiration date of the Renewal Term, which termination shall be effective as of the expiration date of the Renewal Term

### Anti-Assignment

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Consequently either this Agreement or any of the respective rights or obligations of the Parties hereunder may be assigned or otherwise transferred, in whole or in part, in any form whatsoever (including by way of change of Control), by eit
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: the Parties may at any time assign or transfer all or part of its rights and obligations under this Agreement to any of its Affiliates provided that such assignment or transfer is previously notified to the other Party.
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: For purposes of this Agreement, any merger, consolidation, or change of corporate structure following which there is a Change of Control of Kitov shall be considered as an assignment by Kitov, allowing Dexcel to terminate the Agreement as h

Wrong flags (flagged, not labeled):
- *AtnInternationalInc_20191108_10-Q_EX-10.1_11878541_EX-10.1_M*: Vendor may not deliver or obtain any Material or Deliverables from or use any Restricted Entities to provide any Services under this Agreement, without prior written consent from AT&T. Vendor may not use, in connection with any Deliverable,
- *LeadersonlineInc_20000427_S-1A_EX-10.8_4991089_EX-10.8_Co-Br*: Except as otherwise set forth herein, neither Party shall transfer, assign or cede any rights or delegate any obligations hereunder, in whole or in part, whether voluntarily or by operation of law, without the prior written consent of the o
- *CHEETAHMOBILEINC_04_22_2014-EX-10.43-Cooperation Agreement*: With respect to the cooperation hereof, Party B has the discretion to assign to its affiliates all or part of its obligations hereunder without breaching this agreement.

### Change Of Control

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: Notice of Merger or Acquisition. Until the date that this Agreement terminates or is terminated in accordance with Section 15 hereof, ENERGOUS agrees that, [***].
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Consequently either this Agreement or any of the respective rights or obligations of the Parties hereunder may be assigned or otherwise transferred, in whole or in part, in any form whatsoever (including by way of change of Control), by eit
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: nothing in this Agreement shall in any way restrict any change in shareholding or control of the Parties or its Affiliates or the Repairer's rights to delegate obligations of it hereunder to a Subcontractor. provided that, in such case, the

Wrong flags (flagged, not labeled):
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: No assignment or transfer of this Agreement shall be effective as to Transporter unless and until Transporter has been provided written notice thereof.
- *FerroglobePlc_20150624_F-4A_EX-10.20_9154746_EX-10.20_Outsou*: Absorption or fusion of EIT by other companies. In this case, the Customer can decide if he wants to continue working with the new company, which will have to continue rendering all the services convened in this Agreement, in the same condi
- *ANIXABIOSCIENCESINC_06_09_2020-EX-10.1-COLLABORATION AGREEME*: either Party may assign this Agreement without such consent to an entity that acquires all or substantially all of the business or assets of such Party to which this Agreement relates, whether by merger, consolidation, sale of assets or oth

### Governing Law

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: This Letter of Authorization will be governed by and construed in accordance with the laws of California, excluding its conflict of laws provisions, and be subject to the non-exclusive jurisdiction of the California courts.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Pursuant to and in accordance with Section 5-1401 of the New York General Obligations Law, the Parties hereto agree that this Agreement in all respects, and any claim or cause of action based upon or arising out of this Agreement, or any de
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: relating to the subject matter of this Agreement or the transactions contemplated hereby or the Company/Repairer relationship being established, shall be governed by, and construed in accordance with, the laws of the State of New York, U.S.

Wrong flags (flagged, not labeled):
- *NOVOINTEGRATEDSCIENCES,INC_12_23_2019-EX-10.1-JOINT VENTURE *: Arbitration shall be conducted in accordance with the provisions of the Arbitration Act No. 42 of 1965, as amended, and in accordance with such procedure as may be agreed by the Parties or, failing such agreement, in accordance with the rul
- *TELEGLOBEINTERNATIONALHOLDINGSLTD_03_29_2004-EX-10.10-CONSTR*: If any difference shall arise between or among the Parties or any of them in respect of the interpretation or effect of this Agreement or any part or provision thereof or their rights and obligations thereunder, and by reasons thereof there

### Exclusivity

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: If DIALOG decides to discontinue Sales of any Product, it will notify ENERGOUS at least [***] prior to such discontinuance, and following such notification, the exclusivity rights, if any, associated with that Product will cease; provided, 
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: In the event that Zanotti fails to secure purchases amounting to the Minimum Order for any particular period, the exclusive supplier rights granted pursuant to this Article 2 shall become non- exclusive commencing immediately following such
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: If, within five (5) business days of receipt of such notice from Aura, Zanotti does not agree to match such price, the exclusive supplier rights granted pursuant to Article 2 above shall, upon Aura's sole election, immediately become non-ex

Wrong flags (flagged, not labeled):
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: During the Term, PPI and its Affiliates shall not: (i) file for Marketing Authorization with respect to any Competing Product in any country in the Territory, (ii) manufacture or have manufactured any Competing Product in any country in the
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: During the Term, except if PPI is unable to supply Products (including, but not limited to, in connection with EKR's exercise of its rights under Section 17.5 below) or as provided in the Supply Agreement, EKR shall purchase all of its requ
- *AMERICASSHOPPINGMALLINC_12_10_1999-EX-10.2-SITE DEVELOPMENT *: During the term of this Agreement and for a period of two years after the expiration date of this Agreement, HDI shall not participate in any project similar to the Site on the Internet from which products substantially similar to Deerskin 

### Audit Rights

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: Such audit may also not interfere with DIALOG's or its Affliates' quarterly closing of its books.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: The cost of any such audits by the Company's representative(s) shall be borne by the Company unless if, as a result of that audit, the Repairer is found to be in Default, in which cases the cost of such audit will be borne by the Repairer.
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Company's audit: at any time during the Term, the Repairer may: (i) audit the management and the performance of the Company's maintenance activities which are still under Company'sresponsibility; and/or, (ii) arrange for operational visits,

Wrong flags (flagged, not labeled):
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: EKR shall during business hours, on no less than 14 day's notice from PPI and not more than once in any Calendar Year, make available for inspection the records and books referred to in Section 7.2. Such inspection shall be undertaken by an
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: Transporter reserves the right to witness calibration of these devices, and Shipper shall notify Transporter at least 48 hours prior to the initiation of such calibration procedures.
- *ENERGYXXILTD_05_08_2015-EX-10.13-Transportation AGREEMENT*: Transporter or its authorized representative shall have access to the platform from which shipments are received for the purpose of examining and checking meters and other installations utilized in connection with the handling of Crude Petr

### Insurance

Missed (labeled, not flagged):
- *ENERGOUSCORP_03_16_2017-EX-10.24-STRATEGIC ALLIANCE AGREEMEN*: Each party will, at the other party's request, provide to the other party a certificate of insurance evidencing the foregoing insurance coverage.
- *AURASYSTEMSINC_06_16_2010-EX-10.25-STRATEGIC ALLIANCE AGREEM*: Such policy or policies will (a) have aggregate limits of liability of not less than $1,000,000 with respect to any incident or occurrence and of not less than $2,000,000 in the aggregate; (b) name both Zanotti and Aura as insured parties; 
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: Without prejudice to any term and condition under this Agreement, the Company shall maintain in force, at all times during the Term and [*****], at its own costs and expenses, with insurers of internationally recognized

Wrong flags (flagged, not labeled):
- *ParatekPharmaceuticalsInc_20170505_10-KA_EX-10.29_10323872_E*: Further, Supplier shall at a minimum retain [* * *].
- *VerizonAbsLlc_20200123_8-K_EX-10.4_11952335_EX-10.4_Service *: Section 3.1 Engagement. The Issuer engages Cellco as the Servicer of the Receivables for the Issuer and the Indenture Trustee, and Cellco accepts this engagement.

### Warranty Duration

Missed (labeled, not flagged):
- *AzulSa_20170303_F-1A_EX-10.3_9943903_EX-10.3_Maintenance Agr*: For used LRUs and Main Elements repaired and overhauled by the Repairer, the warranty period shall start on the date of Delivery and shall end [*****] thereafter, whichever occurs the earliest, and such warranty shall be subject to the excl
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: Kitov shall provide Dexcel with written notification of any shortfalls in shipment quantity, and (a) any out-of-specification temperature excursions based on the downloaded data logger information following compliance with the provisions of
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: In the event that a defect is not apparent upon visual inspection during the shelf life of the Product ("Hidden Defect"), Kitov shall use commercially reasonably best efforts to provide Dexcel with written notification within thirty (30) Wo

Wrong flags (flagged, not labeled):
- *KitovPharmaLtd_20190326_20-F_EX-4.15_11584449_EX-4.15_Manufa*: Dexcel shall supply the Product with at least **** percent (****%) of the shelf life upon Delivery unless otherwise agreed by the Parties.
- *NANOPHASETECHNOLOGIESCORP_11_01_2005-EX-99.1-DISTRIBUTOR AGR*: NTC shall further grant to ALFA AESAR the same warranty, as set forth in NTC's General Terms and Conditions of Sale for its products set forth in Schedule B.
- *PACIRA PHARMACEUTICALS, INC. - A_R STRATEGIC LICENSING, DIST*: PPI represents and warrants that: (i) on the Agreement Date, EKR shall receive sole ownership of, and good and valid title to, the Transferred Equipment, free and clear of any liens and encumbrances, (ii) the Transferred Equipment as of the
