# BIG BOY FUNCTION


# ----------------------------------------------SEGMENTED DATA--------------------------------------------------




def segmented_data_test(CLIENT_ACCOUNT_ID, DAYS_DATA, EXCEL_NAME, SEGMENT, METRIC):    
    import sys
    import time

    import pandas as pd
    from twitter_ads.client import Client
    from twitter_ads.campaign import LineItem
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
    line_items = list(account.line_items(None))

    # the list of metrics we want to fetch, for a full list of possible metrics
    # see: https://dev.twitter.com/ads/analytics/metrics-and-segmentation
    # metric_groups = [METRIC_GROUP.BILLING]
#     metric_groups = [METRIC_GROUP.ENGAGEMENT]
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
        queued_job_ids.append(LineItem.queue_async_stats_job(account, chunk_ids, metric_groups, segmentation).id)

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

    # Pulling Segmented data. 45 Days limit. This only pulls campaigns that actually have segment data!
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
    dates.append(pd.date_range(end=end_date, periods=DAYS_DATA))  
    df3 = pd.DataFrame(df['vals'].to_list(), columns=dates[0].date)
    big = pd.concat([df, df3], axis = 1)

    # CREATED LINK FOR NAME AND ID FOR FUTURE REFERENCE
    # MANIPULATING BIG DF

    df_linker = pd.DataFrame(columns=['name', 'id'])
    df_linker['name'] = [i.name for i in list(account.line_items())]
    df_linker['id'] = [i.id for i in list(account.line_items())]
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
    test_fixed_collapse['new_vals'] = my_list
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


    test_fixed_collapse.to_excel(f"{EXCEL_NAME}.xlsx", index = False)
    print(f"--- Excel Created --- {EXCEL_NAME}.xlsx")
    return test_fixed_collapse
















# --------------------------------------------------------------------------------------------------------------------------






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












