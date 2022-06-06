import boto3
import requests
import os
from requests_aws4auth import AWS4Auth
import json


def get_role_session(environment, role):
    account = {"sirius-dev": "288342028542", "digideps-dev": "248804316466"}
    client = boto3.client("sts")

    role_to_assume = f"arn:aws:iam::{account[environment]}:role/{role}"
    response = client.assume_role(
        RoleArn=role_to_assume, RoleSessionName="deputy_reporting_script"
    )

    session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    return session


def get_request_auth(credentials):
    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token

    auth = AWS4Auth(
        access_key,
        secret_key,
        "eu-west-1",
        "execute-api",
        session_token=token,
    )

    return auth


def get_report_payload(latest_s3_ref):
    payload = {
        "report": {
            "data": {
                "type": "reports",
                "attributes": {
                    "submission_id": 12346,
                    "reporting_period_from": "2020-01-01",
                    "reporting_period_to": "2020-12-31",
                    "year": 2020,
                    "date_submitted": "2020-01-03T09:30:00.001Z",
                    "type": "PF",
                },
                "file": {
                    "name": "Report_1234567T_2018_2019_11112.pdf",
                    "mimetype": "application/pdf",
                    "s3_reference": latest_s3_ref,
                },
            }
        }
    }
    return payload


def get_supporting_payload():
    payload = {
        "supporting_document": {
            "data": {
                "type": "supportingdocuments",
                "attributes": {"submission_id": 12345},
                "file": {
                    "name": "supportdoc.pdf",
                    "mimetype": "application/pdf",
                    "source": "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akzjxEi4DKnGNJ4oUU3FQNod5KrW5jnUufc+x8ant1X3/37084dqqSOsfcG+rh5vTvO3z9f0XPmvqxc48gppaSteufIBbzZm+Ky8hY/v/fnOtu77Suub3XV56SmWonzvs09fuvIS9SXer0b5KhXDtuFpydJ/TSiMHUskYVLltjFpLiOtSYzVm/HWxZOHXDAkGpJonqbom2np6eabwtrNU3dBu+t1NdkjN3JR5E4e1018VFKcUqYvM4h63Ajuc64hkeA+5ujFOWWHTh89ajeUJGSl8rWOLW27drFtk2/vnvBWpMQRameM9vG11Bu71fxSsgzkEJ6r/L2LReVcPJtZASuRI3hKFHl+avDcHOqaFi3ztzgbQusHQv09a4Jqj+lZMpHB/wTwRApwPIBPnrqQhyhP8Jk8U1b9uMW+8Ta7er7///0te7EKZW5kc3RyZWFtCmVuZG9iagoxNCAwIG9iagozNzU3CmVuZG9iagoxNSAwIG9iagooVW50aXRsZWQgNSkKZW5kb2JqCjE2IDAgb2JqCihNYWMgT1MgWCAxMC4xMy42IFF1YXJ0eiBQREZDb250ZXh0KQplbmRvYmoKMTcgMCBvYmoKKFRleHRFZGl0KQplbmRvYmoKMTggMCBvYmoKKEQ6MjAyMDA0MDMwODE0MTdaMDAnMDAnKQplbmRvYmoKMTkgMCBvYmoKKCkKZW5kb2JqCjIwIDAgb2JqClsgXQplbmRvYmoKMSAwIG9iago8PCAvVGl0bGUgMTUgMCBSIC9Qcm9kdWNlciAxNiAwIFIgL0NyZWF0b3IgMTcgMCBSIC9DcmVhdGlvbkRhdGUgMTggMCBSIC9Nb2REYXRlCjE4IDAgUiAvS2V5d29yZHMgMTkgMCBSIC9BQVBMOktleXdvcmRzIDIwIDAgUiA+PgplbmRvYmoKeHJlZgowIDIxCjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwODY1NSAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCjAwMDAwMDM5NjkgMDAwMDAgbiAKMDAwMDAwMDAyMiAwMDAwMCBuIAowMDAwMDAwMjIzIDAwMDAwIG4gCjAwMDAwMDAzNDYgMDAwMDAgbiAKMDAwMDAwMzkzNCAwMDAwMCBuIAowMDAwMDA0MTAyIDAwMDAwIG4gCjAwMDAwMDA0NDMgMDAwMDAgbiAKMDAwMDAwMzkxMyAwMDAwMCBuIAowMDAwMDA0MDUyIDAwMDAwIG4gCjAwMDAwMDQzNDcgMDAwMDAgbiAKMDAwMDAwNDU5NyAwMDAwMCBuIAowMDAwMDA4NDQ0IDAwMDAwIG4gCjAwMDAwMDg0NjUgMDAwMDAgbiAKMDAwMDAwODQ5NCAwMDAwMCBuIAowMDAwMDA4NTQ3IDAwMDAwIG4gCjAwMDAwMDg1NzQgMDAwMDAgbiAKMDAwMDAwODYxNiAwMDAwMCBuIAowMDAwMDA4NjM1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgMjEgL1Jvb3QgMTEgMCBSIC9JbmZvIDEgMCBSIC9JRCBbIDw0ZmE4NTU1ZDAxMDQyZGZmOWYyMzNmMzRjMDJiN2JhYT4KPDRmYTg1NTVkMDEwNDJkZmY5ZjIzM2YzNGMwMmI3YmFhPiBdID4+CnN0YXJ0eHJlZgo4Nzk5CiUlRU9GCg==",
                },
            }
        }
    }
    return payload


def get_checklist_payload():
    payload = {
        "checklist": {
            "data": {
                "type": "checklists",
                "attributes": {
                    "submission_id": 12345,
                    "submitter_email": "donald.duck@digital.justice.gov.uk",
                    "reporting_period_from": "2019-01-01",
                    "reporting_period_to": "2019-12-31",
                    "year": 2019,
                    "type": "PF",
                },
                "file": {
                    "name": "Checklist.pdf",
                    "mimetype": "application/pdf",
                    "source": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJlYW0KeAFFjrsOgkAQRXu/4pRL4TLDCgutxsaOZBILY0WwwwTW/49DLKxu7iMnd2VkJTfktotJUubUKppiN3RJ2WbuvKkvRZkKQpl8LnHIfZJePBCOf7tzshymhbOhza92bVHFFmozh2MvHgSrPFXCXO2IhlA+FU/sxtX81fgFNj0hZgplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKMTI3CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMyAwIFIgL1Jlc291cmNlcyA2IDAgUiAvQ29udGVudHMgNCAwIFIgL01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjYgMCBvYmoKPDwgL1Byb2NTZXQgWyAvUERGIC9UZXh0IF0gL0NvbG9yU3BhY2UgPDwgL0NzMSA3IDAgUiA+PiAvRm9udCA8PCAvVFQxIDggMCBSCj4+ID4+CmVuZG9iago5IDAgb2JqCjw8IC9MZW5ndGggMTAgMCBSIC9OIDEgL0FsdGVybmF0ZSAvRGV2aWNlR3JheSAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJlYW0KeAGlVwdYk9caPv9IwkrYU0bYyDKg7BmZAWQPQVRiEkgYIQaCgLgoxQrWLQ4cFS2KUrRaESgu1OKgblDruFBLBaUWq7iwes8JoND2ufc+z83/HP73fGd86z3ffwBAXciVSLJxAECOOF8aEstOnpmcwqTdAwpAF6gCR6DK5eVJ2NHREXAKEOeKBeg98feyC2BIcsMB7TVx7L/2KHxBHg/OOgVbET+PlwMA5g0ArY8nkeYDoGgB5eYL8iUIh0KslRUfGwBxKgAKKqNroRiYhAjEAqmIxwyRcouYIdycHC7T2dGZGS3NTRdl/4PVaNH/88vJliG70c8ENpW8rLhw+HaE9pfxuYEIu0N8mMcNihvFjwtEiZEQ+wOAm0nyp8dCHAbxPFlWAhtie4jr06XBCRD7QnxbKAtFeBoAhE6xMD4JYmOIw8TzIqMg9oRYyMsLSIHYBuIaoYCD8gRjRlwU5XPiIYb6iKfS3Fg03xYA0psvCAwakZPpWbnhyAYzKP8uryAOyeU2FwsDkJ1QF9mVyQ2LhtgK4heC7BA0H+5DMZDkR6M9YZ8SKM6ORHr9Ia4S5Mn9hX1KV74wHuXMGQCqWb40Hq2FtlHj00XBHIiDIS4USkORHPpLPSHJlvMMxoT6TiqLRb5DH2nBAnECiiHixVKuNCgEYhgrWitIxLhAAHLBPPiXB8SgBzBBHhCBAjnKAFyQAxsTWmAPWwicJYZNCmfkgSwoz4C49+M46qMVaI0EjuSCdDgzG64bkzIBH64fWYf2yIUN9dC+ffJ9eaP6HKG+AOOvgQyOC8EAHBdCNAN0yyWF0L4c2A+AUhkcy4B4vBZnyCNnEC23dcQGNI609I9qyYUr+HJdI+uQlyO2BUCbxaAYjiHb5J6TuiSLnAqbFxlB+pAsuTYpnFEEHORyb7lsTOsnz5Fv/R+1zoe2jvd+fLzGYnwaxisf7pwNPRSPxicPWvMO2p01uvpTNOUa1xjIbCSSqlUxnDm1couR78xS6VwR78rqwf+QtU/ZGtPuMCFvUeN5IWcK/2+8gLoo1ylXKQ8oNwETvn+hdFL6ILpLuQefOx/tiR7HBxR7xBwR/CuCPo4xYIRZPLkE5SIbPigvf7fzU85G9vnLDhgh14s4y5bvghiWAxvKrECe1xConwvzkQejLYM8RdxwgIwZn7sRLeNOQHtJqx5gdq08dQEw69Waz8u1yKPdSTal3lBpL0kXrzGQSObUlgwLJJ9GUR4EyyNfRoJSe9Yh1gBrD6ue9Zz14NMM1i3Wb6xO1i448oRYTxwljhPNRAvRAZiw10KcJprlqJ5ohc+3H9dNZPjIOZrIcMQ33iijkY/5o5waz/1xHsrjNRYtNH8sU5mjJ3U891B8xzMGZex/s2h8RidWhJHsyE8dw5zhxKAxbBkuDDYDY5jCx5nhD5E5w4wRwdCFo6EMa0YgY9LHeIyccWQHOu+IYWN14VMVS4ajY0xA/gkhD6TymsUd9fevPjIneIkqmmj8qcLo8GSOaBqpCWM6x+IqZ8iEk5UANYnAAmiHFMYVnXYxrCXMCXNQJUZVCDISmyXP4T+cBNKYdCI5sDJFASbJJl1I/1GMqpU3fFCtGqneDqQfHPUlA0l3VMfGewB3H4kXqmj/bP34kyGgelKtqUFUa/necu+ogdRQajBgUp2QnDqFGgaxB5qVLyiEdw8AAnIlRVJRhjCfyYa3HAGTI+Y52jOdWU7w64buTGgOAM9j5HchTKeDJ5MWjMhI9KIAJXif0gL68KtqDr/WDtArN+AFv5lB8A4QBeJBMpgD/RDCTEphZEvAMlAOKsEasBFsBTvBHlAHGsBhcAy0gtPgB3AJXAWd4C78nvSCJ2AQvATDGIbRMDqmieljJpglZoc5Y+6YLxaERWCxWDKWhmVgYkyGlWCfYZXYOmwrtgurw77FmrHT2AXsGnYH68H6sT+wtziBq+BauBFuhU/B3XE2Ho7H47PxDHw+XoyX4avwzXgNXo834qfxS3gn3o0/wYcIQCgTOoQp4UC4EwFEFJFCpBNSYjFRQVQRNUQDrAHtxA2imxgg3pBUUpNkkg4wi6FkAskj55OLyZXkVnIf2UieJW+QPeQg+Z5CpxhS7CieFA5lJiWDsoBSTqmi1FKOUs7BCt1LeUmlUnVgftxg3pKpmdSF1JXU7dSD1FPUa9SH1CEajaZPs6P50KJoXFo+rZy2hVZPO0m7TuulvVZQVjBRcFYIVkhRECuUKlQp7Fc4oXBd4ZHCsKKaoqWip2KUIl+xSHG14h7FFsUrir2Kw0rqStZKPkrxSplKy5Q2KzUonVO6p/RcWVnZTNlDOUZZpLxUebPyIeXzyj3Kb1Q0VGxVAlRSVWQqq1T2qpxSuaPynE6nW9H96Sn0fPoqeh39DP0B/TVDk+HI4DD4jCWMakYj4zrjqaqiqqUqW3WOarFqleoR1SuqA2qKalZqAWpctcVq1WrNarfUhtQ11Z3Uo9Rz1Feq71e/oN6nQdOw0gjS4GuUaezWOKPxUJPQNNcM0ORpfqa5R/OcZq8WVctai6OVqVWp9Y3WZa1BbQ3tadqJ2oXa1drHtbt1CB0rHY5Ots5qncM6XTpvdY102boC3RW6DbrXdV/pTdLz1xPoVegd1OvUe6vP1A/Sz9Jfq39M/74BaWBrEGOwwGCHwTmDgUlak7wm8SZVTDo86SdD3NDWMNZwoeFuww7DISNjoxAjidEWozNGA8Y6xv7GmcYbjE8Y95tomviaiEw2mJw0eczUZrKZ2czNzLPMQVND01BTmeku08umw2bWZglmpWYHze6bK5m7m6ebbzBvMx+0MLGYYVFiccDiJ0tFS3dLoeUmy3bLV1bWVklWy62OWfVZ61lzrIutD1jfs6Hb+NnMt6mxuTmZOtl9ctbk7ZOv2uK2LrZC22rbK3a4naudyG673TV7ir2Hvdi+xv6Wg4oD26HA4YBDj6OOY4RjqeMxx6dTLKakTFk7pX3Ke5YLKxt+3e46aTiFOZU6tTj94WzrzHOudr45lT41eOqSqU1Tn02zmyaYtmPabRdNlxkuy13aXP50dXOVuja49rtZuKW5bXO75a7lHu2+0v28B8VjuscSj1aPN56unvmehz1/93LwyvLa79Xnbe0t8N7j/dDHzIfrs8un25fpm+b7lW+3n6kf16/G72d/c3++f63/I/Zkdia7nv10Omu6dPrR6a8CPAMWBZwKJAJDAisCLwdpBCUEbQ16EGwWnBF8IHgwxCVkYcipUEpoeOja0FscIw6PU8cZDHMLWxR2NlwlPC58a/jPEbYR0oiWGfiMsBnrZ9yLtIwURx6LAlGcqPVR96Oto+dHfx9DjYmOqY75NdYptiS2PU4zbm7c/riX8dPjV8ffTbBJkCW0JaompibWJb5KCkxal9Q9c8rMRTMvJRski5KbUmgpiSm1KUOzgmZtnNWb6pJanto123p24ewLcwzmZM85Pld1LnfukTRKWlLa/rR33ChuDXdoHmfetnmDvADeJt4Tvj9/A79f4CNYJ3iU7pO+Lr0vwydjfUa/0E9YJRwQBYi2ip5lhmbuzHyVFZW1N+tDdlL2wRyFnLScZrGGOEt8Ntc4tzD3msROUi7pnu85f+P8QWm4tDYPy5ud15SvBf/B7JDZyD6X9RT4FlQXvF6QuOBIoXqhuLCjyLZoRdGj4uDirxeSC3kL20pMS5aV9CxiL9q1GFs8b3HbEvMlZUt6l4Ys3bdMaVnWsh9LWaXrSl98lvRZS5lR2dKyh5+HfH6gnFEuLb+13Gv5zi/IL0RfXF4xdcWWFe8r+BUXK1mVVZXvVvJWXvzS6cvNX35Ylb7q8mrX1TvWUNeI13St9Vu7b536uuJ1D9fPWN+4gbmhYsOLjXM3XqiaVrVzk9Im2abuzRGbm7ZYbFmz5d1W4dbO6unVB7cZblux7dV2/vbrO/x3NOw02lm58+1Xoq9u7wrZ1VhjVVO1m7q7YPevexL3tH/t/nVdrUFtZe2fe8V7u/fF7jtb51ZXt99w/+oD+AHZgf761Pqr3wR+09Tg0LDroM7BykPgkOzQ42/Tvu06HH647Yj7kYbvLL/bdlTzaEUj1ljUOHhMeKy7KbnpWnNYc1uLV8vR7x2/39tq2lp9XPv46hNKJ8pOfDhZfHLolOTUwOmM0w/b5rbdPTPzzM2zMWcvnws/d/6H4B/OtLPbT573Od96wfNC80X3i8cuuV5q7HDpOPqjy49HL7tebrzidqXpqsfVlmve105c97t++kbgjR9ucm5e6ozsvNaV0HX7Vuqt7tv82313su88+6ngp+G7S+ElvuK+2v2qB4YPav41+V8Hu127j/cE9nT8HPfz3Ye8h09+yfvlXW/Zr/Rfqx6ZPKrrc+5r7Q/uv/p41uPeJ5InwwPlv6n/tu2pzdPvfvf/vWNw5mDvM+mzD3+sfK7/fO+LaS/ahqKHHrzMeTn8quK1/ut9b9zftL9NevtoeME72rvNf07+s+V9+Pt7H3I+fPg3LV3wHAplbmRzdHJlYW0KZW5kb2JqCjEwIDAgb2JqCjMzNjcKZW5kb2JqCjcgMCBvYmoKWyAvSUNDQmFzZWQgOSAwIFIgXQplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZXMgL01lZGlhQm94IFswIDAgNTk1IDg0Ml0gL0NvdW50IDEgL0tpZHMgWyAyIDAgUiBdID4+CmVuZG9iagoxMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMyAwIFIgPj4KZW5kb2JqCjggMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1RydWVUeXBlIC9CYXNlRm9udCAvRkxKVFlQK0hlbHZldGljYSAvRm9udERlc2NyaXB0b3IKMTIgMCBSIC9FbmNvZGluZyAvTWFjUm9tYW5FbmNvZGluZyAvRmlyc3RDaGFyIDg0IC9MYXN0Q2hhciAxMTYgL1dpZHRocyBbIDYxMQowIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDU1NiAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDUwMCAyNzggXSA+PgplbmRvYmoKMTIgMCBvYmoKPDwgL1R5cGUgL0ZvbnREZXNjcmlwdG9yIC9Gb250TmFtZSAvRkxKVFlQK0hlbHZldGljYSAvRmxhZ3MgMzIgL0ZvbnRCQm94IFstOTUxIC00ODEgMTQ0NSAxMTIyXQovSXRhbGljQW5nbGUgMCAvQXNjZW50IDc3MCAvRGVzY2VudCAtMjMwIC9DYXBIZWlnaHQgNzE3IC9TdGVtViA5OCAvWEhlaWdodAo1MjMgL1N0ZW1IIDg1IC9BdmdXaWR0aCA0NDEgL01heFdpZHRoIDE1MDAgL0ZvbnRGaWxlMiAxMyAwIFIgPj4KZW5kb2JqCjEzIDAgb2JqCjw8IC9MZW5ndGggMTQgMCBSIC9MZW5ndGgxIDYzMDggL0ZpbHRlciAvRmxhdGVEZWNvZGUgPj4Kc3RyZWFtCngBvVl7dBPXmf/uPDTyW7ItS5Ytj4axJNvy22AscLBsS7bBxjGYh+RgIhnL2AQ3Dhg3ThfWyYZuMYSEkhAgPWlot4RHKYNhiQwN63CSEna3LWkbEtKcbdM8mtMTL7tZ6EkC9uw3I1vFnJLDH5zMPfd+r/v47u/7ZjRz1b9hUwgSYAhoaGkL9nWBepkqkXSv6Q32ReTkN5G2rRnot0ZkNgeAXt/Vt7Y3ImufBYi1rF0/ODU+pRiA+Xl3KNgZscNNpOXdqIjIZDbS7O7e/kcjcvIppKnrH14zZU/JRjm+N/jo1PrwPsrWbwV7Q5H+JhPS7L6HN/ZHZONnSPP7NoSm+hMf+vdrIKhl4fsQAw8BBxTosLQDcJ/GWoBBq2LH6+3qjIQHkyqvg16ryg8ufjqiXxv331+Ebjridmm/REXMdH+FanInc9FFgvbxuF1RizoOGzYMrc4wLMRahXUOVqez2gRD5CA8g/UlrDT0kO0wiHUb1n1YmSh3GKVRsn2E0brPkEEwk0XuOIZflprOm2Lj+N+EiebUi/wV04dnSTpG7wOSPpIAMdWx5CXyQ+gEnvwEbOQxaIAcsv9k7no+gKbD0Id1CCuttoQcHskq5c+RfLAxBMfYIYshp/k/lxTwH5eEKTLCn3eEGSSvZaHkTuLHLC/y/2ZZy5/DejRiOpKLPU7zhy3r+d1ZYbJ/hP++JUxwzK4I2WTBoaf53tw9fGeJam/aE6aOjvAutK9wx/HlFQI/x/IRX+QIawnKBZYmPq/kl3w2DsRuVpzU5tbzmZbd/Dw0ZVm8jnlYz5Ij5AXIIy+M2BbxZ5DF7Z5cmFuxJ0y+c7Ihp8QWJo+5yxty9uQ2OGy5Tbwtt87hQH7Fm9yT3ANcNVfKObkczs4JXAaXqk3W6rSJ2nhtrFar5cLkpyNVvOYsOQpVCMvRk1qNlg2Tn6GSOUuOqcpjr2gZLaUFbWpY/iMmL4HUMDl6SqdwyJzWqJwmTI6djKiOuXlG4RjVoKMUHhtsgSJaChaBRJ4Ka2Br2kCVqSp5gd5V57lTE1At063zzpeJWKQ9ja0+6YjFL5UqjGzxT3c3TTN3pP2b0BSqcToblw6eHOhb1+UNid6A6A1hDUjbB7pN0lCH1XpiXZ9isEq0PdCxpluhwZDUJ4Y80jrRYz0xoI67zdylmAdEzwno8i7znehyhzwjA+4Brxj0+E921Gxon7HWtuhaG2r+zlo1ymQblLU61HG3rdWumDuUtdqVtdqVtTrcHepayua9Pa01G/sxO63enkarlNMqLVzS5pOsQb8nTA6i0rMJ2DHQsa9CDjsEZqYIeAD5Ctb3FDq5XP6EvQC6yV75f+n5GNRRpVKTVZUwBk/BC3AcNHAI+RxYDXvhIlmH9/YqOAWXSRYU4rOXgTA0wX8SWX4LuuBfsH8/nIfn4ATE45heMKB1J7HJj6HsRr4DnpR/BNlQAd+FV8GFs+6EcfmwfBKtS2E5HIGjOP4/iEidYFLkn8kfgRaW4JxPouUtuUk+DsmQDzXQgton4Ryx0e/J3WCC+ejdD+CHcABeg8/IE+SU3C0PyJfkDzBVTZAJrVg2k1PkA/o48135B/Jf5ElEIgfycNUA7IYf4/zHsYzho9VLHiL9ZDd5jnJTT1CnmK2scXICcciFeiwN8DB8DxEYhdfhc/iSXKVMtI7up9+Q58j/B3HQiLtUdhKCASz/jGUn7uks0ZBiUktayGbyLHmO/JbKo5ZTPurb1KPUJ3QzvYoepH/LbGRG2B3sXk3c5HX5rHxBfhuMYIEHYANswd2dh0twDb4iNM6VSWxkPqkhq7EMkReoUXKAjFItZIxcoo6QP5APyVVyg2KpeMpAOal+ajd1lDpP/YruoZ+j99F/oK8zC1iKPcB+rLFxv5/smNw2+St5vvyB/AU+YrUgYGRqoBkehCDutg9mwz/iLo5hOY5Rex3egItq+ZBkwjh8gSgASSZmUkoWY2km95Mu0kNeJGewnFN9+SuFgaBiKD1lpDKpVqqD6qWGqLepITqDzqMX0W30cSxv0pfpG/QNhmVSGANTzyyEHUwvsx/LQeYQM8L8mnWxC9hmdgU7xG5jd9Br2LfYy5otmp2aEc1Vzf/gY7GJe5jbgdG5iDn7Guby3y6GZKP3pfAtWEM8pAP2YDQOkCAMY3Z1ku8hXn2QI7fTW+h6qhiz4Rx8B7N1P2yGbfQqOCC/Sx+BdzBT1uOUQ/AyUwMW9nmMzhNQjFk0Vdy5ebk5DrstW5wlWPGRn5lhTjcZ0wypKcl6XUJ8XGyMltOwDE0RyPeKdQGrZA9IjF1saChQZDGIiuAtigDeylapbmYfyaqMC6JpRk839uy6rac70tMd7Ul01kqoLMi3ekWr9EuPaA2TtiU+5J/yiH6rNK7yi1X+GZVPQF4QcIDVa+r2WCUSsHqluoHuYW/AU5BPRt0IR2xBvvLgcEOcMrEEtcHN+ICFWqWHVzKLHq+ULiKPNtrmDXZKLUt8Xk+GIPhRh6qlPlyjIL9HQj9he3yn2Lk97IaOgMIFV/kkOuiXqIAyl94pGUWPZHzsY9PfxGnOu+MWo0TZ6oKh4TrJHdiO4CpiQJGCO1BqbLXitNRWv08iW6ecUHxch54q7kZ+E2yBdVYpRqwRu4fXBRBcWOobMbvN6sNXghbfSLo7XRUK8kdNW+YLuPvRguqCaoXOF0xbIvTP/xTR/2ZMoaYtr/8RaePSKABEQUBciH5K1jXqIiI6W6E0oQoYXlOBOOHlJ7jNHvSnVqIwZ2ibxNoWBqWh1mk3uj0R5wLrPCMx6Wb1R6jGj/0Dw7p5GCnsrxOtw9fx1zogjn82UxOc0mhsuuugGJVAR3NFIsFpfkD5sbThrrtNYrcS3wE1piiLJu8tCpQVaBSfpVT8AW/xCZLVjwp8m8xvDENMi+8EITv9YSJvDYPHMorvqPSDq9Gcr6RajwfXR6EgHxV5AnKF+dY6XLlOyRXrsHV4Yeewtc7ajcnE2FSKhtCwvwgRbPUhTrAMV3T7M6JsyO+fh/MUKfPgEOw+7McZ1k3NgFRVFU1gp+J8/DGl7S2+JT5pyJMhuT1+jAKm71iLTxrDzPX7sVdJ1FP0eHOPacrnUvS5JA/tZZFZ8N1lCKfwDw8rc7b6REEaGx7OGFbut4gcJnC7wj2lCIPSRYE8TIZacCwSUchQYyCIArrlVzCdjSk9nVH4zv71CJdH/caRc9HbchXhinuEsOtuEJ53VwjPj3o6A+FK9Hm+gvB93xzCC2YgXPX1CLujfqOT1eitW0W45h4hXHs3CHvuCmFv1NMZCNehz14F4fpvDuGGGQgv/HqEF0X9Ricb0dtFKsJN9wjhxXeDcPNdIXx/1NMZCLegz/crCC/55hBeOgPh1q9HeFnUb3RyOXq7TEV4xT1CeOXdIOy7K4T9UU9nINyGPvsVhB+IIuzOkODW5/DQbY9duOcP5lW3QI5vSmwy1DAfgsBshAb8qK6hXPiGr3xK48c0XvH4ldGEdBm+gUc0qvoODXUHvaKm8csscpXj220hlUitxhfwGjzbuoTfgjSeKdVGznm0RWFgsGp1YYBLWBUZefp95JFySGmkMe/DGRwFsMJ5BmdikRaXlOkFvQNrDbMzfPNP7Ktf1YaZxTfw3AC9F3Cti7gWB7PdZqLJAo5itDFGoxluULSNZW5o0rU7Vpuczbpri69VTlRea/aGPJ9AVVXl4onKkmJiEPSiXpjDXJzU//uknn31+Fefs4nHlT3R0CC/x5jx6yATvyRtJN49+Lx2n/llnmYTqSQ21ZCYnGRIdce7U7W5ZtIYd5q+QH5BX8h4V3sl5jL/rvip8VMx7oL+QjK1SssK2Un70yzZLg3HpQmWTC7WkhZn457PfDnzlcx3MhlbWpItk02Pjef0iY4ki4M1O7ILOUd6ut3xO+FgO55ENF9bPPFRs+6vi8d/N+FKdrn0WJNdRe24k/GqceRwb7px1JYU1w6660BkWBo/vQjLaHi7XpesS9Gl6hhNvG1WRrYdrGCxkyxLjJGzQ5wh0U4SEkWzgCoWG60p1g4JOmzwSM7pJLpKp1Opzjxn3uPkkXZ4pL0d0oxYDEIWKSudWz63LJFwGk4jzgK9DsqI3WEXZ2k4Qp26XFGerLt5lX3m+aeWFaee4O4vWTpYvfTNyb8Q058IH5ez6Ng/HGKJyNQ/tHzJ+kU/+vEb7eX183cVtmTqiIjfnxSpmbRvqnvi5DBRDjiV3JLfoU8zjXgqUEQK3U9XxOxl9yTvS91r2Junycm2OcqFOqE+u96xInuloyt7rX0wfjBhMHFA7M/ut/XbD2Ydyk+hcctsAVOYAmZDhjHTZChILcxJiuvR2m3lNso2KyGWcaaYfpFpSeEYS+F+Z1wRF5OoozgoEorMvCnN5DAuyLFzjhxzSSLv0C0AR2F6cclINE7j1yZcSqQmXDrklEC5irDVu1xKsDBaGCaj6xE1UE2kgLIbbGa7kMgLEIPHbYTOx6Rm85CzJKMuI9UkEGvSLAGEWYkJWkesQOy2mFhSwAh4xopNlj5TIOlp2Kjh0lVirNSGKNFTr8ehvZ20p2DEykrL58x22IuUEM2ZXV5WakzjxEi4DKnGNJ4oUU3FQNod5KrW5jnUufc+x8ant1X3/37084dqqSOsfcG+rh5vTvO3z9f0XPmvqxc48gppaSteufIBbzZm+Ky8hY/v/fnOtu77Suub3XV56SmWonzvs09fuvIS9SXer0b5KhXDtuFpydJ/TSiMHUskYVLltjFpLiOtSYzVm/HWxZOHXDAkGpJonqbom2np6eabwtrNU3dBu+t1NdkjN3JR5E4e1018VFKcUqYvM4h63Ajuc64hkeA+5ujFOWWHTh89ajeUJGSl8rWOLW27drFtk2/vnvBWpMQRameM9vG11Bu71fxSsgzkEJ6r/L2LReVcPJtZASuRI3hKFHl+avDcHOqaFi3ztzgbQusHQv09a4Jqj+lZMpHB/wTwRApwPIBPnrqQhyhP8Jk8U1b9uMW+8Ta7er7///0te7EKZW5kc3RyZWFtCmVuZG9iagoxNCAwIG9iagozNzU3CmVuZG9iagoxNSAwIG9iagooVW50aXRsZWQgNSkKZW5kb2JqCjE2IDAgb2JqCihNYWMgT1MgWCAxMC4xMy42IFF1YXJ0eiBQREZDb250ZXh0KQplbmRvYmoKMTcgMCBvYmoKKFRleHRFZGl0KQplbmRvYmoKMTggMCBvYmoKKEQ6MjAyMDA0MDMwODE0MTdaMDAnMDAnKQplbmRvYmoKMTkgMCBvYmoKKCkKZW5kb2JqCjIwIDAgb2JqClsgXQplbmRvYmoKMSAwIG9iago8PCAvVGl0bGUgMTUgMCBSIC9Qcm9kdWNlciAxNiAwIFIgL0NyZWF0b3IgMTcgMCBSIC9DcmVhdGlvbkRhdGUgMTggMCBSIC9Nb2REYXRlCjE4IDAgUiAvS2V5d29yZHMgMTkgMCBSIC9BQVBMOktleXdvcmRzIDIwIDAgUiA+PgplbmRvYmoKeHJlZgowIDIxCjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwODY1NSAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCjAwMDAwMDM5NjkgMDAwMDAgbiAKMDAwMDAwMDAyMiAwMDAwMCBuIAowMDAwMDAwMjIzIDAwMDAwIG4gCjAwMDAwMDAzNDYgMDAwMDAgbiAKMDAwMDAwMzkzNCAwMDAwMCBuIAowMDAwMDA0MTAyIDAwMDAwIG4gCjAwMDAwMDA0NDMgMDAwMDAgbiAKMDAwMDAwMzkxMyAwMDAwMCBuIAowMDAwMDA0MDUyIDAwMDAwIG4gCjAwMDAwMDQzNDcgMDAwMDAgbiAKMDAwMDAwNDU5NyAwMDAwMCBuIAowMDAwMDA4NDQ0IDAwMDAwIG4gCjAwMDAwMDg0NjUgMDAwMDAgbiAKMDAwMDAwODQ5NCAwMDAwMCBuIAowMDAwMDA4NTQ3IDAwMDAwIG4gCjAwMDAwMDg1NzQgMDAwMDAgbiAKMDAwMDAwODYxNiAwMDAwMCBuIAowMDAwMDA4NjM1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgMjEgL1Jvb3QgMTEgMCBSIC9JbmZvIDEgMCBSIC9JRCBbIDw0ZmE4NTU1ZDAxMDQyZGZmOWYyMzNmMzRjMDJiN2JhYT4KPDRmYTg1NTVkMDEwNDJkZmY5ZjIzM2YzNGMwMmI3YmFhPiBdID4+CnN0YXJ0eHJlZgo4Nzk5CiUlRU9GCg==",
                },
            }
        }
    }
    return payload


def handle_request(method, url, auth, payload, headers):
    body = json.dumps(payload)
    response = requests.request(
        method=method, url=url, auth=auth, data=body, headers=headers
    )
    print(response.text)
    print(response.status_code)

    return response.json(), response.status_code


def get_latest_s3_ref(bucket, account, role):
    session = get_role_session(account, role)
    s3 = session.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)

    files_in_bucket = []

    if "Contents" not in resp:
        print(f"ERROR: No files in {bucket}")
        os._exit(1)

    for obj in resp["Contents"]:
        files_in_bucket.append(obj["Key"])

    return files_in_bucket[0]


def validate_response(
    status, expected_status, request_type, method, response, is_parent
):
    if status == expected_status:
        print(f"Successfully performed {request_type} request")
    else:
        print(f"Stopping as {request_type} {method} failed")
        os._exit(1)

    parent_id = None
    if is_parent:
        if "data" in response and "id" in response["data"]:
            parent_id = response["data"]["id"]
        else:
            print("Stopping as report response is invalid")
            os._exit(1)

    return parent_id


def main():
    latest_s3_ref = get_latest_s3_ref(
        "pa-uploads-branch-replication", "digideps-dev", "breakglass"
    )

    headers = {
        "Content-Type": "application/json",
    }
    branch_prefix = "ddpb9999"
    casereference = "63120095"
    ver = "v2"

    session = get_role_session("sirius-dev", "breakglass")
    credentials = session.get_credentials()
    auth = get_request_auth(credentials)

    report_payload = get_report_payload(latest_s3_ref)
    report_url = f"https://dev.deputy-reporting.api.opg.service.justice.gov.uk/{ver}/clients/{casereference}/reports"
    response, status = handle_request("POST", report_url, auth, report_payload, headers)
    parent_id = validate_response(status, 201, "annual report", "POST", response, True)

    supporting_payload = get_supporting_payload()
    supporting_url = f"https://dev.deputy-reporting.api.opg.service.justice.gov.uk/{ver}/clients/{casereference}/reports/{parent_id}/supportingdocuments"
    response, status = handle_request(
        "POST", supporting_url, auth, supporting_payload, headers
    )
    validate_response(status, 201, "supporting document", "POST", response, False)

    checklist_payload = get_checklist_payload()
    checklist_url = f"https://dev.deputy-reporting.api.opg.service.justice.gov.uk/{ver}/clients/{casereference}/reports/{parent_id}/checklists"
    response, status = handle_request(
        "POST", checklist_url, auth, checklist_payload, headers
    )
    checklist_id = validate_response(status, 201, "checklist", "POST", response, True)

    checklist_url_put = f"https://dev.deputy-reporting.api.opg.service.justice.gov.uk/{ver}/clients/{casereference}/reports/{parent_id}/checklists/{checklist_id}"
    response, status = handle_request(
        "PUT", checklist_url_put, auth, checklist_payload, headers
    )
    validate_response(status, 200, "checklist override", "PUT", response, False)


if __name__ == "__main__":
    main()
