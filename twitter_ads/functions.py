# BIG BOY FUNCTION

def send_email(SUBJECT, BODY, SEND_TO, EXCEL_FILE, ID, DD, SEG):
    from twitter_ads.functions import big_merge_all
    import appscript
    from appscript import app, k
    from mactypes import Alias
    from pathlib import Path
    import base64
    
    
    big_merge_all(
                            CLIENT_ACCOUNT_ID=ID,
                            DAYS_DATA=DD,
                            SEGMENT=SEG, 
                            BIG_EXCEL_NAME=EXCEL_FILE
                                            
                    )
    
    

    import os
    f = open(os.path.expanduser(f"~/OneDrive - Mark1 Media & Consulting/Documents - Copy/Datorama/Twitter API/{EXCEL_FILE}.xlsx"))

    
    
    
    
    def create_message_with_attachment():
        subject = SUBJECT
        body = BODY
        to_recip = SEND_TO
        msg = Message(subject=subject, body=body, to_recip=to_recip)

        # attach file
        p = Path(f'{f.name}')
        msg.add_attachment(p)
#         msg.show()
        msg.send()

    class Outlook(object):
        def __init__(self):
            self.client = app('Microsoft Outlook')

    class Message(object):
        def __init__(self, parent=None, subject='', body='', to_recip=[], cc_recip=[], show_=True):

            if parent is None: parent = Outlook()
            client = parent.client

            self.msg = client.make(
                new=k.outgoing_message,
                with_properties={k.subject: subject, k.content: body})

            self.add_recipients(emails=to_recip, type_='to')
            self.add_recipients(emails=cc_recip, type_='cc')

#             if show_: self.show()

#         def show(self):
    #         self.msg.open()
#             self.msg.activate()
    #         

        def send(self):
            self.msg.send()

        def add_attachment(self, p):
            # p is a Path() obj, could also pass string

            p = Alias(str(p)) # convert string/path obj to POSIX/mactypes path

            attach = self.msg.make(new=k.attachment, with_properties={k.file: p})

        def add_recipients(self, emails, type_='to'):
            if not isinstance(emails, list): emails = [emails]
            for email in emails:
                self.add_recipient(email=email, type_=type_)

        def add_recipient(self, email, type_='to'):
            msg = self.msg

            if type_ == 'to':
                recipient = k.to_recipient
            elif type_ == 'cc':
                recipient = k.cc_recipient

            msg.make(new=recipient, with_properties={k.email_address: {k.address: email}})

    return create_message_with_attachment()




# ----------------------------------------------SEGMENTED DATA--------------------------------------------------




# def segmented_data_test(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME, SEGMENT, METRIC):    
#     import sys
#     import time

#     import pandas as pd
#     from twitter_ads.client import Client
#     from twitter_ads.campaign import LineItem
#     from twitter_ads.enum import METRIC_GROUP
#     from twitter_ads.enum import SEGMENTATION_TYPE
#     from twitter_ads.utils import split_list

#     CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
#     CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
#     ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
#     ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
#     ACCOUNT_ID = CLIENT_ACCOUNT_ID

#     # initialize the client
#     client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

#     # load the advertiser account instance
#     account = client.accounts(ACCOUNT_ID)

#     # grab the line items from Cursor
#     line_items = list(account.line_items(None))

#     # the list of metrics we want to fetch, for a full list of possible metrics
#     # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
#     # metric_groups = [METRIC_GROUP.BILLING]
# #     metric_groups = [METRIC_GROUP.ENGAGEMENT]
#     metric_groups = [METRIC]
#     segmentation = [SEGMENT]
#     # fetching stats on the instance
#     # line_items[0].stats(metric_groups)

#     # fetching stats for multiple line items
#     ids = list(map(lambda x: x.id, line_items))
#     if not ids:
#         print('Error: A minimum of 1 items must be provided for entity_ids')
#         sys.exit()

#     # sync_data = []
#     # # Sync/Async endpoint can handle max 20 entity IDs per request
#     # # so split the ids list into multiple requests
#     # for chunk_ids in split_list(ids, 20):
#     #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

#     # print(sync_data)

#     # create async stats jobs and get job ids
#     queued_job_ids = []
#     for chunk_ids in split_list(ids, 20):
#         queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups, segmentation).id)

#     # print(queued_job_ids)

#     # let the job complete
#     seconds = 30
#     time.sleep(seconds)

#     async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

#     async_data = []
#     for result in async_stats_job_results:
#         async_data.append(LineItem.async_stats_job_data(account, url=result.url))

#     # print(async_data)

#     # make one big list
#     result = []
#     for i in async_data:
#         result.append(i['data'])

#     # flatten the list
#     flat_list = [item for sublist in result for item in sublist]

#     # Pulling Segmented data. 45 Days limit. This only pulls campaigns that actually have segment data!
#     list_cols = ['name', 'id', 'metric', 'segment', 'total', 'vals']
#     summation = []
#     vals = []
#     segments = []
#     # dates = []
#     ids_ = []
#     metrics_list = []
#     appended_data = []
#     br = []
#     num = 0
#     while num <= len(flat_list)-1:
#         if flat_list[num]['id_data']:
#             num2 = 0
#             while num2 <= len(flat_list[num]['id_data'])-1:
#                 for key ,value in flat_list[num]['id_data'][num2]['metrics'].items():
#                     if type(value) != list:
#                         value = [0]
#                     csiti = flat_list[num]['id']
#                     seg = flat_list[num]['id_data'][num2]['segment']['segment_name']
#                     units = value
#                     end_date = pd.to_datetime('today').normalize()
#                     df = pd.DataFrame(columns=list_cols)
#                     metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
#                     summation.append(sum(value))
#                     if len(value) < DAYS_DATA:
#                         value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

#                     vals.append(value)
#                     ids_.append(csiti)
#                     segments.append(seg)

#                 num2 += 1
#         num += 1 

#     metrics_list = [item for sublist in metrics_list for item in sublist][:len(ids_)]
#     df['id'] = ids_
#     df['total'] = summation
#     df['vals'] = vals
#     df['metric'] = metrics_list
#     df['segment'] = segments

#     dates = []
#     end_date = pd.to_datetime('today').normalize()
#     dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
#     df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
#     big = pd.concat([df, df3], axis = 1)

#     # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE
#     # MANIPULATING BIG DF

#     df_linker = pd.DataFrame(columns=['name', 'id'])
#     df_linker['name'] = [i.name for i in list(account.line_items())]
#     df_linker['id'] = [i.id for i in list(account.line_items())]
#     big2 = big.merge(df_linker, how='left', on='id')
#     big2.drop(columns=['name_x'], axis=1, inplace=True)
#     first_column = big2.pop('name_y')
#     big2.insert(0, 'name_y', first_column)
#     big2.drop(columns=['vals'], axis=1, inplace=True)
#     big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
#     big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric', 'segment': 'Segment'}, inplace=True)
    
#     def df_column_switch(df, column1, column2):
#         i = list(df.columns)
#         a, b = i.index(column1), i.index(column2)
#         i[b], i[a] = i[a], i[b]
#         df = df[i]
#         return df

#     big2 = df_column_switch(big2, 'Segment', 'Metric')
#     big2 = df_column_switch(big2, 'Metric', 'Total')
# #     big3 = big2.iloc[: , -46:].T
# #     big3.columns = list(big2['CampaignName'].values)

#     bb = big2.copy()
#     bb = bb.melt(['CampaignName', 'id', 'Segment', 'Total', 'Metric'], var_name='Date', value_name='Day')
#     bb = df_column_switch(bb, 'Metric', 'Date')
# #     bb.head(200)

#     test = bb.copy()
#     test_fixed_collapse = test.iloc[::len(test['Metric'].unique()), :]
#     my_list = list(test['Day'])
# #     my_list
#     def chunks(list_in, n):
#         # For item i in a range that is a length of l,
#         for i in range(0, len(list_in), n):
#             # Create an index range for l of n items:
#             yield list_in[i:i+n]

#     my_list = list(chunks(my_list, len(test['Metric'].unique())))
#     # my_list
#     test_fixed_collapse['new_vals'] = my_list
#     # test_fixed_collapse



#     new_cols = list(test['Metric'].unique())
#     split_df = pd.DataFrame(test_fixed_collapse['new_vals'].tolist(), columns=[new_cols])
# #     split_df

#     test_fixed_collapse.reset_index(drop=True, inplace=True)
#     def convertTuple(tup):
#             # initialize an empty string
#         str = ''
#         for item in tup:
#             str = str + item
#         return str
#     test_fixed_collapse = test_fixed_collapse.iloc[:,:7]
#     for c in split_df.columns:
#     #     print(convertTuple(c))
#         test_fixed_collapse[convertTuple(c)] = split_df[convertTuple(c)]

#     test_fixed_collapse = test_fixed_collapse.drop(columns=['Day', 'Metric', 'Total']) 
# #     test_fixed_collapse


# #     test_fixed_collapse.to_excel(f"{EXCEL_NAME}.xlsx", index = False)
# #     print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
#     return test_fixed_collapse



def segmented_data_test(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME, SEGMENT, METRIC):    
    import sys
    import time

    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.campaign import Campaign
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.enum import SEGMENTATION_TYPE
    from twitter_ads.utils import split_list

    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID

    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.campaigns(None))

    metric_groups = [METRIC]
    segmentation = [SEGMENT]
        # fetching stats on the instance
        # line_items[0].stats(metric_groups)

        # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

        # sync_data = []
        # # Sync/Async endpoint can handle max 20 entity IDs per request
        # # so split the ids list into multiple requests
        # for chunk_ids in split_list(ids, 20):
        #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

        # print(sync_data)

        # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
    #     queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups, segmentation).id)
        queued_job_ids.append(Campaign.queue_async_stats_job(account, chunk_ids, metric_groups, segmentation).id)

        # print(queued_job_ids)

        # let the job complete
    seconds = 30
    time.sleep(seconds)

    # async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)
    async_stats_job_results = Campaign.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
    #     async_data.append(LineItem.async_stats_job_data(account, url=result.url))
        async_data.append(Campaign.async_stats_job_data(account, url=result.url))

        # print(async_data)

        # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

        # flatten the list
    flat_list = [item for sublist in result for item in sublist]
#     return flat_list
#     Pulling Segmented data. 45 Days limit. This only pulls campaigns that actually have segment data!
    list_cols = ['name', 'id', 'metric', 'segment', 'total', 'vals']
    summation = []
    vals = []
    segments = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0
    while num <= len(flat_list)-1:
        if flat_list[num]['id_data']:
            num2 = 0
            while num2 <= len(flat_list[num]['id_data'])-1:
                for key ,value in flat_list[num]['id_data'][num2]['metrics'].items():
                    if type(value) != list:
                        value = [0]
                    csiti = flat_list[num]['id']
                    seg = flat_list[num]['id_data'][num2]['segment']['segment_name']
                    units = value
                    end_date = pd.to_datetime('today').normalize()
                    df = pd.DataFrame(columns=list_cols)
                    metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
                    summation.append(sum(value))
                    if len(value) < DAYS_DATA:
                        value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

                    vals.append(value)
                    ids_.append(csiti)
                    segments.append(seg)

                num2 += 1
        num += 1 

    metrics_list = [item for sublist in metrics_list for item in sublist][:len(ids_)]
    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = metrics_list
    df['segment'] = segments

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA+1))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date[:-1])
    big = pd.concat([df, df3], axis = 1)
#     return big
    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE
    # MANIPULATING BIG DF

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.campaigns())]
    df_linker['id'] = [i.id for i in list(account.campaigns())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric', 'segment': 'Segment'}, inplace=True)
    
    def df_column_switch(df, column1, column2):
        i = list(df.columns)
        a, b = i.index(column1), i.index(column2)
        i[b], i[a] = i[a], i[b]
        df = df[i]
        return df

    big2 = df_column_switch(big2, 'Segment', 'Metric')
    big2 = df_column_switch(big2, 'Metric', 'Total')
#     big3 = big2.iloc[: , -46:].T
#     big3.columns = list(big2['CampaignName'].values)

    bb = big2.copy()
    bb = bb.melt(['CampaignName', 'id', 'Segment', 'Total', 'Metric'], var_name='Date', value_name='Day')
    bb = df_column_switch(bb, 'Metric', 'Date')
#     bb.head(200)

    test = bb.copy()
    test_fixed_collapse = test.iloc[::len(test['Metric'].unique()), :]
    my_list = list(test['Day'])
#     my_list
    def chunks(list_in, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(list_in), n):
            # Create an index range for l of n items:
            yield list_in[i:i+n]

    my_list = list(chunks(my_list, len(test['Metric'].unique())))
    # my_list
#     print(test_fixed_collapse.loc[:, ('new_vals')])
    test_fixed_collapse['new_vals'] = my_list
    
#     print(test_fixed_collapse.columns)
#     print(my_list)
    # test_fixed_collapse



    new_cols = list(test['Metric'].unique())
    split_df = pd.DataFrame(test_fixed_collapse['new_vals'].tolist(), columns=[new_cols])
#     split_df

    test_fixed_collapse.reset_index(drop=True, inplace=True)
    def convertTuple(tup):
            # initialize an empty string
        str = ''
        for item in tup:
            str = str + item
        return str
    test_fixed_collapse = test_fixed_collapse.iloc[:,:7]
    for c in split_df.columns:
    #     print(convertTuple(c))
        test_fixed_collapse[convertTuple(c)] = split_df[convertTuple(c)]

    test_fixed_collapse = test_fixed_collapse.drop(columns=['Day', 'Metric', 'Total']) 
#     test_fixed_collapse


#     test_fixed_collapse.to_excel(f"{EXCEL_NAME}.xlsx", index = False)
#     print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return test_fixed_collapse












# --------------------------------------------------------------------------------------------------------------------------


def big_merge_all(CLIENT_ACCOUNT_ID, DAYS_DATA, SEGMENT, BIG_EXCEL_NAME):
    import pandas as pd
    from twitter_ads.functions import fetch_and_fix_engagement_data
    from twitter_ads.functions import fetch_and_fix_billing_data
    from twitter_ads.functions import fetch_and_fix_video_data
    from twitter_ads.functions import fetch_and_fix_media_data
    from twitter_ads.functions import fetch_and_fix_ltv_mobile_conversion_data
    from twitter_ads.functions import segmented_data_test
#     Engagement Data
    bb1 = segmented_data_test(
                            CLIENT_ACCOUNT_ID=CLIENT_ACCOUNT_ID,
                            DAYS_DATA=DAYS_DATA,
                            EXCEL_NAME="Sample_Excel(bb1)",
                            SEGMENT=SEGMENT,
                            METRIC='ENGAGEMENT'
    )
#     Video Data
    bb2 = segmented_data_test(
                            CLIENT_ACCOUNT_ID=CLIENT_ACCOUNT_ID,
                            DAYS_DATA=DAYS_DATA,
                            EXCEL_NAME="Sample_Excel(bb2)",
                            SEGMENT=SEGMENT,
                            METRIC='VIDEO'
    )
#     Billing Data
#     bb3 = segmented_data_test(
#                             CLIENT_ACCOUNT_ID=CLIENT_ACCOUNT_ID,
#                             DAYS_DATA=DAYS_DATA,
#                             EXCEL_NAME="Mazda_Age_Billing",
#                             SEGMENT=SEGMENT,
#                             METRIC='BILLING'
#     )
#     Merge DataFrames
    result = pd.concat([bb1, bb2], axis=1)
#     result = pd.concat([result, bb3], axis=1)
    result = result.loc[:,~result.columns.duplicated()]
    result.fillna(0, inplace=True)
    result.to_excel(f"{BIG_EXCEL_NAME}.xlsx", index=False)
    print(f'DONE ---- Big Excel Created ---- {BIG_EXCEL_NAME}.xlsx')
    return result




# ----------------------------------------------ENGAGEMENT--------------------------------------------------












def fetch_and_fix_engagement_data(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME):
        
#     Importing dependancies
    import sys
    import time
    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.utils import split_list

#     Defining API Key variables
    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID
    
    # M1
    # ACCOUNT_ID = '18ce53vlqsy'
    # Mazda
    # ACCOUNT_ID = '18ce55ci5bt'
    # Solidarity
#     ACCOUNT_ID = '18ce55drkgj'


    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
    metric_groups = [METRIC_GROUP.ENGAGEMENT]

    # fetching stats on the instance
    # line_items[0].stats(metric_groups)

    # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

    # sync_data = []
    # # Sync/Async endpoint can handle max 20 entity IDs per request
    # # so split the ids list into multiple requests
    # for chunk_ids in split_list(ids, 20):
    #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

    # print(sync_data)

    # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups).id)

    # print(queued_job_ids)

    # let the job complete
    seconds = 30
    time.sleep(seconds)

    async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
        async_data.append(LineItem.async_stats_job_data(account, url=result.url))

    # print(async_data)

    # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

    # flatten the list
    flat_list = [item for sublist in result for item in sublist]
    
    
    
    # Iterators and empty lists to append into
    list_cols = ['name', 'id', 'metric', 'total', 'vals']
    summation = []
    vals = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0

    # going through each line item and fixing the data
    while num <= len(flat_list)-1:
        for key ,value in flat_list[num]['id_data'][0]['metrics'].items():
            if type(value) != list:
                value = [0]

            csiti = flat_list[num]['id']
            units = value
            end_date = pd.to_datetime('today').normalize()
    #         dates.append(pd.date_range(end=end_date, periods=len(units)))  

            df = pd.DataFrame(columns=list_cols)
            metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
            summation.append(sum(value))

            if len(value) < DAYS_DATA:
                value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

            vals.append(value)
            ids_.append(csiti)

        num += 1

    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = [item for sublist in metrics_list for item in sublist][:len(ids_)]

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
#     b
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric'}, inplace=True)
    big2.to_excel(f"{EXCEL_NAME}.xlsx")
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return big2












# ----------------------------------------------BILLING--------------------------------------------------












def fetch_and_fix_billing_data(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME):
        
#     Importing dependancies
    import sys
    import time
    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.utils import split_list

#     Defining API Key variables
    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID
    
    # M1
    # ACCOUNT_ID = '18ce53vlqsy'
    # Mazda
    # ACCOUNT_ID = '18ce55ci5bt'
    # Solidarity
#     ACCOUNT_ID = '18ce55drkgj'


    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
    metric_groups = [METRIC_GROUP.BILLING]

    # fetching stats on the instance
    # line_items[0].stats(metric_groups)

    # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

    # sync_data = []
    # # Sync/Async endpoint can handle max 20 entity IDs per request
    # # so split the ids list into multiple requests
    # for chunk_ids in split_list(ids, 20):
    #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

    # print(sync_data)

    # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups).id)

    # print(queued_job_ids)

    # let the job complete
    seconds = 30
    time.sleep(seconds)

    async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
        async_data.append(LineItem.async_stats_job_data(account, url=result.url))

    # print(async_data)

    # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

    # flatten the list
    flat_list = [item for sublist in result for item in sublist]
    
    
    
    # Iterators and empty lists to append into
    list_cols = ['name', 'id', 'metric', 'total', 'vals']
    summation = []
    vals = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0

    # going through each line item and fixing the data
    while num <= len(flat_list)-1:
        for key ,value in flat_list[num]['id_data'][0]['metrics'].items():
            if type(value) != list:
                value = [0]

            csiti = flat_list[num]['id']
            units = value
            end_date = pd.to_datetime('today').normalize()
    #         dates.append(pd.date_range(end=end_date, periods=len(units)))  

            df = pd.DataFrame(columns=list_cols)
            metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
            summation.append(sum(value))

            if len(value) < DAYS_DATA:
                value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

            vals.append(value)
            ids_.append(csiti)

        num += 1

    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = [item for sublist in metrics_list for item in sublist][:len(ids_)]

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
#     b
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric'}, inplace=True)
    big2.to_excel(f"{EXCEL_NAME}.xlsx")
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return big2












# ----------------------------------------------VIDEO--------------------------------------------------











def fetch_and_fix_video_data(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME):
        
#     Importing dependancies
    import sys
    import time
    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.utils import split_list

#     Defining API Key variables
    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID
    
    # M1
    # ACCOUNT_ID = '18ce53vlqsy'
    # Mazda
    # ACCOUNT_ID = '18ce55ci5bt'
    # Solidarity
#     ACCOUNT_ID = '18ce55drkgj'


    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
    metric_groups = [METRIC_GROUP.VIDEO]

    # fetching stats on the instance
    # line_items[0].stats(metric_groups)

    # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

    # sync_data = []
    # # Sync/Async endpoint can handle max 20 entity IDs per request
    # # so split the ids list into multiple requests
    # for chunk_ids in split_list(ids, 20):
    #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

    # print(sync_data)

    # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups).id)

    # print(queued_job_ids)

    # let the job complete
    seconds = 30
    time.sleep(seconds)

    async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
        async_data.append(LineItem.async_stats_job_data(account, url=result.url))

    # print(async_data)

    # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

    # flatten the list
    flat_list = [item for sublist in result for item in sublist]
    
    
    
    # Iterators and empty lists to append into
    list_cols = ['name', 'id', 'metric', 'total', 'vals']
    summation = []
    vals = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0

    # going through each line item and fixing the data
    while num <= len(flat_list)-1:
        for key ,value in flat_list[num]['id_data'][0]['metrics'].items():
            if type(value) != list:
                value = [0]

            csiti = flat_list[num]['id']
            units = value
            end_date = pd.to_datetime('today').normalize()
    #         dates.append(pd.date_range(end=end_date, periods=len(units)))  

            df = pd.DataFrame(columns=list_cols)
            metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
            summation.append(sum(value))

            if len(value) < DAYS_DATA:
                value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

            vals.append(value)
            ids_.append(csiti)

        num += 1

    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = [item for sublist in metrics_list for item in sublist][:len(ids_)]

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
#     b
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric'}, inplace=True)
    big2.to_excel(f"{EXCEL_NAME}.xlsx")
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return big2












# ----------------------------------------------MEDIA--------------------------------------------------











def fetch_and_fix_media_data(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME):
        
#     Importing dependancies
    import sys
    import time
    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.utils import split_list

#     Defining API Key variables
    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID
    
    # M1
    # ACCOUNT_ID = '18ce53vlqsy'
    # Mazda
    # ACCOUNT_ID = '18ce55ci5bt'
    # Solidarity
#     ACCOUNT_ID = '18ce55drkgj'


    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
    metric_groups = [METRIC_GROUP.MEDIA]

    # fetching stats on the instance
    # line_items[0].stats(metric_groups)

    # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

    # sync_data = []
    # # Sync/Async endpoint can handle max 20 entity IDs per request
    # # so split the ids list into multiple requests
    # for chunk_ids in split_list(ids, 20):
    #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

    # print(sync_data)

    # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups).id)

    # print(queued_job_ids)

    # let the job complete
    seconds = 30
    time.sleep(seconds)

    async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
        async_data.append(LineItem.async_stats_job_data(account, url=result.url))

    # print(async_data)

    # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

    # flatten the list
    flat_list = [item for sublist in result for item in sublist]
    
    
    
    # Iterators and empty lists to append into
    list_cols = ['name', 'id', 'metric', 'total', 'vals']
    summation = []
    vals = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0

    # going through each line item and fixing the data
    while num <= len(flat_list)-1:
        for key ,value in flat_list[num]['id_data'][0]['metrics'].items():
            if type(value) != list:
                value = [0]

            csiti = flat_list[num]['id']
            units = value
            end_date = pd.to_datetime('today').normalize()
    #         dates.append(pd.date_range(end=end_date, periods=len(units)))  

            df = pd.DataFrame(columns=list_cols)
            metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
            summation.append(sum(value))

            if len(value) < DAYS_DATA:
                value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

            vals.append(value)
            ids_.append(csiti)

        num += 1

    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = [item for sublist in metrics_list for item in sublist][:len(ids_)]

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
#     b
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric'}, inplace=True)
    big2.to_excel(f"{EXCEL_NAME}.xlsx")
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return big2










# ----------------------------------------------LIFE_TIME_VALUE_MOBILE_CONVERSION--------------------------------------------------











def fetch_and_fix_ltv_mobile_conversion_data(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME):
        
#     Importing dependancies
    import sys
    import time
    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
    from twitter_ads.enum import METRIC_GROUP
    from twitter_ads.utils import split_list

#     Defining API Key variables
    CONSUMER_KEY = 'thomtSuw3LzIc5RsLMdsROUsF'
    CONSUMER_SECRET = 'EBCTwmejJ8erIHxvTbfghLiBAznaCMkJGEjmRW19DJQolEbNna'
    ACCESS_TOKEN = '1316796142169063429-IfRrzjYPQ0NVEpkLSct46KdiAEW7WY'
    ACCESS_TOKEN_SECRET = 'k5z4pGkDMiEfLjfkAbztJYZWqj84kXgGUpLKAdBQnjLiS'
    ACCOUNT_ID = CLIENT_ACCOUNT_ID
    
    # M1
    # ACCOUNT_ID = '18ce53vlqsy'
    # Mazda
    # ACCOUNT_ID = '18ce55ci5bt'
    # Solidarity
#     ACCOUNT_ID = '18ce55drkgj'


    # initialize the client
    client = Client(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # load the advertiser account instance
    account = client.accounts(ACCOUNT_ID)

    # grab the line items from Cursor
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
    metric_groups = [METRIC_GROUP.LIFE_TIME_VALUE_MOBILE_CONVERSION]

    # fetching stats on the instance
    # line_items[0].stats(metric_groups)

    # fetching stats for multiple line items
    ids = list(map(lambda x: x.id, line_items))
    if not ids:
        print('Error: A minimum of 1 items must be provided for entity_ids')
        sys.exit()

    # sync_data = []
    # # Sync/Async endpoint can handle max 20 entity IDs per request
    # # so split the ids list into multiple requests
    # for chunk_ids in split_list(ids, 20):
    #     sync_data.append(LineItem.all_stats(account, chunk_ids, metric_groups))

    # print(sync_data)

    # create async stats jobs and get job ids
    queued_job_ids = []
    for chunk_ids in split_list(ids, 20):
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups).id)

    # print(queued_job_ids)

    # let the job complete
    seconds = 30
    time.sleep(seconds)

    async_stats_job_results = LineItem.async_stats_job_result(account, job_ids=queued_job_ids)

    async_data = []
    for result in async_stats_job_results:
        async_data.append(LineItem.async_stats_job_data(account, url=result.url))

    # print(async_data)

    # make one big list
    result = []
    for i in async_data:
        result.append(i['data'])

    # flatten the list
    flat_list = [item for sublist in result for item in sublist]
    
    
    
    # Iterators and empty lists to append into
    list_cols = ['name', 'id', 'metric', 'total', 'vals']
    summation = []
    vals = []
    # dates = []
    ids_ = []
    metrics_list = []
    appended_data = []
    br = []
    num = 0

    # going through each line item and fixing the data
    while num <= len(flat_list)-1:
        for key ,value in flat_list[num]['id_data'][0]['metrics'].items():
            if type(value) != list:
                value = [0]

            csiti = flat_list[num]['id']
            units = value
            end_date = pd.to_datetime('today').normalize()
    #         dates.append(pd.date_range(end=end_date, periods=len(units)))  

            df = pd.DataFrame(columns=list_cols)
            metrics_list.append([k for k, v in flat_list[num]['id_data'][0]['metrics'].items()])
            summation.append(sum(value))

            if len(value) < DAYS_DATA:
                value = (value + [0] * DAYS_DATA)[:DAYS_DATA-1]

            vals.append(value)
            ids_.append(csiti)

        num += 1

    df['id'] = ids_
    df['total'] = summation
    df['vals'] = vals
    df['metric'] = [item for sublist in metrics_list for item in sublist][:len(ids_)]

    dates = []
    end_date = pd.to_datetime('today').normalize()
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
    big2 = big.merge(df_linker, how='left', on='id')
    big2.drop(columns=['name_x'], axis=1, inplace=True)
    first_column = big2.pop('name_y')
    big2.insert(0, 'name_y', first_column)
    big2.drop(columns=['vals'], axis=1, inplace=True)
#     b
    big2.iloc[: , -1] = big2.iloc[: , -1].fillna(0).astype("int32")
    big2.rename(columns={'name_y': 'CampaignName', 'total': 'Total', 'metric': 'Metric'}, inplace=True)
    big2.to_excel(f"{EXCEL_NAME}.xlsx")
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return big2












